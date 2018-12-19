#!/usr/bin/python

import os
import time
import select
import signal
import multiprocessing as mp

from contextlib import contextmanager

import pyinotify

from ram.process import running_ps
from ram.process import output
from ram.process import _quote_cmd
from ram.osutils import match_name


class WatchTimeoutError(Exception):
    pass


class Watch(object):
    def __init__(self, iopipe):
        self.iopipe = iopipe

    def fileno(self):
        return self.iopipe.fileno()

    def __nonzero__(self):
        return self.status()

    def __iter__(self):
        while self:
            try:
                data = self(0)
            except WatchTimeoutError:
                break
            else:
                yield data

    def select(self, timeout=None):
        return any(select.select([self.fileno()], [], [], timeout))

    def status(self):
        raise NotImplementedError()

    def update(self):
        raise NotImplementedError()

    def __call__(self, timeout=None, iterate=True):
        ready = self.select(timeout)

        if not ready:
            raise WatchTimeoutError("watch timed out.")
        elif iterate:
            return self.update()
        else:
            return None


class PipeWatch(Watch):
    def __init__(self, iopipe):
        super(PipeWatch, self).__init__(iopipe)
        self.eofile = False

    def status(self):
        return not self.eofile

    def update(self):
        data = ''
        while self.select(0):
            try:
                buff = os.read((self.fileno()), 4096)
            except OSError:
                buff = ''

            if buff:
                data += buff
            else:
                self.eofile = True
                break

        return data


class ExitWatch(Watch):
    def __init__(self, ioproc):
        self.ioproc = ioproc

    def fileno(self):
        return self.ioproc.stdin.fileno()

    def status(self):
        return self.ioproc.poll() is None

    def select(self, timeout=None):
        if timeout is None:
            return self.ioproc.wait() is not None
        else:
            ready = super(ExitWatch, self).select(timeout)
            while ready and self:
                time.sleep(0.001)
            return ready

    def update(self):
        return self.ioproc.poll()


def watch_status(command, *args):
    return running_ps(command, *args, wait=False, wrap=ExitWatch)


def watch_stdout(command, *args):
    return running_ps(command, *args, wait=False, wrap=lambda p: PipeWatch(p.stdout))


def watch_stderr(command, *args):
    return running_ps(command, *args, wait=False, wrap=lambda p: PipeWatch(p.stderr))


class IterWatch(Watch):
    def __init__(self, iopipe, ioproc):
        super(IterWatch, self).__init__(iopipe)
        self.ioproc = ioproc

    def status(self):
        return self.ioproc.exitcode is None

    def update(self):
        exc, obj, _tb = self.iopipe.recv()
        if exc:
            self.ioproc.terminate()
            _ev = str(obj) + _tb.rstrip()
            raise exc(_ev)
        else:
            return obj


def _process_exc():
    from sys import exc_info
    from traceback import format_exc

    exc_type, exc_val, exc_tb = exc_info()
    exc_proc = "Process: %s\n" % mp.current_process().name
    return exc_type, exc_val, "\n" + exc_proc + format_exc()


@contextmanager
def watch_iterable(iterable, name=None):
    r_pipe, w_pipe = mp.Pipe(duplex=False)

    def _wrap_iter(iterable=iterable, w_pipe=w_pipe):
        try:
            for index, obj in enumerate(iterable):
                w_pipe.send((None, obj, None))
        except BaseException as exc:
            w_pipe.send(_process_exc())
        finally:
            while True:
                signal.pause()

    p = mp.Process(target=_wrap_iter, name=name)
    try:
        p.start()
        yield IterWatch(r_pipe, p)
    finally:
        p.terminate()
        p.join()


_SLEEP_TIMEOUT = 1000.0


def track_output(command, *args, **kwargs):
    timeout = kwargs.pop('timeout', None)
    if timeout is None:
        timeout = _SLEEP_TIMEOUT
    _was_output = None
    while True:
        _now_output = output(command, *args, **kwargs)
        if _now_output != _was_output:
            _was_output = _now_output
            yield _now_output
        time.sleep(timeout / _SLEEP_TIMEOUT)


def watch_output(command, *args, **kwargs):
    kwargs.setdefault('timeout', None)
    return watch_iterable(
        track_output(command, *args, **kwargs),
        name='watch: %s' % _quote_cmd(command, *args)
    )


def track_timer(timeout=None):
    if timeout is None:
        _timeout = 1.0
    else:
        _timeout = timeout / _SLEEP_TIMEOUT
    prev_time = time.time()
    while True:
        next_time = prev_time + _timeout
        sleep_for = next_time - time.time()
        time.sleep(sleep_for % _timeout)
        prev_time = next_time
        yield time.time()


def watch_timer(timeout=None):
    return watch_iterable(
        track_timer(timeout),
        name='timer'
    )


class InotifyProcessEventQueue(pyinotify.ProcessEvent):
    def __init__(self):
        self.queue = []

    def __iter__(self):
        while self.queue:
            yield self.queue.pop(0)

    def process_IN_CREATE(self, event):
        self.queue.append(event)

    def process_IN_DELETE(self, event):
        self.queue.append(event)

    def process_IN_MOVED(self, event):
        self.queue.append(event)


def track_dir(dirname, match=None, files=True, dirs=False, rec=False):
    wm = pyinotify.WatchManager()
    mask = (
        pyinotify.IN_DELETE |
        pyinotify.IN_CREATE |
        pyinotify.IN_MOVED_FROM |
        pyinotify.IN_MOVED_TO
    )

    queue = InotifyProcessEventQueue()

    notifier = pyinotify.Notifier(wm, queue)
    wd = wm.add_watch(dirname, mask, rec=rec, auto_add=rec)

    while True:
        notifier.process_events()

        for event in queue:
            if not dirs and event.mask & pyinotify.IN_ISDIR:
                continue
            if not files and not event.mask & pyinotify.IN_ISDIR:
                continue
            if not match_name(event.name, match):
                continue

            is_deleted = bool(event.mask & (
                pyinotify.IN_DELETE |
                pyinotify.IN_MOVED_FROM
            ))

            is_created = bool(event.mask & (
                pyinotify.IN_CREATE |
                pyinotify.IN_MOVED_TO
            ))

            is_present = is_created if is_created != is_deleted else None

            yield (
                event.path,
                event.name,
                event.dir,
                is_present,
            )

        if notifier.check_events():
            notifier.read_events()


def watch_dir(dirname, match=None, files=True, dirs=False, rec=False):
    return watch_iterable(
        track_dir(dirname, match, files, dirs, rec),
        name='dir'
    )
