#!/usr/bin/python

import os
import sys
import signal
import subprocess

from contextlib import contextmanager

from pipes import quote

from ram.osutils import environ

import ram.options


_shell = ram.options['shell']
_trace = ram.options['trace']


def _quote_cmd(command, *args):
    if not isinstance(command, basestring):
        return " ".join(map(quote, list(command) + list(args)))
    elif args:
        return " ".join(map(quote, [command] + list(args)))
    else:
        return command


# run process in foreground
# cases:
#   signals:
#     - ping terminated by Ctrl+C / no KeyboardInterrupt
#     - ping show status by Ctrl+Q / no interpreter exit
#     - pipe to head doesnt show broken pipe error
#   return codes
#     - successfully terminated program returned 0
#     - errorly terminated program (false) return 1
#     - cat terminated by signal returns 128 + signum

class FgLaunch(object):
    def __init__(self):
        self._signals = {signal.SIGPIPE: signal.SIG_DFL}

    def __enter__(self):
        self._restore = {}
        for signum in self._signals:
            self._restore[signum] = signal.signal(signum, self._signals[signum])
        return self

    def __exit__(self, et, ex, tb):
        for signum in self._restore:
            signal.signal(signum, self._restore[signum])

    def exitcode(self, code):
        return 128 - code if code < 0 else code

    def __call__(self, command, **kwargs):
        if _trace:
            print >> sys.stderr, ": %s" % command,
            print >> sys.stderr, " <<<"
        with self:
            _environ = kwargs.get('environ', {})
            with environ(RAMDEBUG="trace" if _trace else "", **_environ):
                exitcode = self.exitcode(self.exitwith(self.runshell(command)))
        if _trace:
            print >> sys.stderr, ": %s" % command,
            print >> sys.stderr, " >>> = %s" % exitcode

        return exitcode


class SystemLaunch(FgLaunch):
    def exitwith(self, status):
        return (
            -os.WTERMSIG(status)
            if os.WIFSIGNALED(status) else
            os.WEXITSTATUS(status)
            if os.WIFEXITED(status) else
            None
        )

    def runshell(self, command):
        return os.system(command)


class SubprocessLaunch(FgLaunch):
    def __init__(self):
        super(SubprocessLaunch, self).__init__()
        self._signals[signal.SIGINT] = signal.SIG_IGN
        self._signals[signal.SIGQUIT] = signal.SIG_IGN

    def exitwith(self, status):
        return status

    def _preexec(self):
        for signum in self._signals:
            signal.signal(signum, signal.SIG_DFL)

    def runshell(self, command):
        return subprocess.call(command, preexec_fn=self._preexec, shell=True)


class ProcessError(RuntimeError):
    pass


def _run_fg(command, *args, **kwargs):
    fnproc = SystemLaunch() if _shell else SubprocessLaunch()
    return fnproc(_quote_cmd(command, *args), **kwargs)


def launch(command, *args, **kwargs):
    return _run_fg(command, *args, **kwargs)


def invoke(command, *args, **kwargs):
    status = launch(command, *args, **kwargs)
    if status:
        raise ProcessError(status)


def _run_ps(command, *args, **kwargs):
    _environ = kwargs.pop('environ', {})
    _usepipe = kwargs.pop('usepipe', False)
    _preexec = kwargs.pop('preexec', None)

    _stdin = kwargs.pop('stdin', None)
    _stdout = kwargs.pop('stdout', None)
    _stderr = kwargs.pop('stderr', None)

    pipe = subprocess.PIPE if _usepipe else None

    stdin = subprocess.PIPE if _stdin or _usepipe else None
    stdout = subprocess.PIPE if _stdout or _usepipe else None
    stderr = subprocess.PIPE if _stderr or _usepipe else None

    with environ(RAMDEBUG="trace" if _trace else "", **_environ):
        return subprocess.Popen(
            _quote_cmd(command, *args), preexec_fn=_preexec,
            stdin=stdin, stdout=stdout, stderr=stderr,
            universal_newlines=True, shell=True,
        )


def run(command, *args, **kwargs):
    _input = kwargs.pop('input', None)
    proc = _run_ps(command, *args, usepipe=True, **kwargs)

    output, errors = proc.communicate(_input)
    status = proc.returncode

    return status, output, errors


def output(command, *args, **kwargs):
    status, output, errors = run(command, *args, **kwargs)
    if status:
        raise RuntimeError(errors)
    else:
        return output


@contextmanager
def running_ps(command, *args, **kwargs):
    wait = kwargs.pop('wait', None)
    wrap = kwargs.pop('wrap', lambda _: _)

    proc = _run_ps(command, *args, usepipe=not wait, **kwargs)
    try:
        yield wrap(proc)
    except Exception:
        wait = False

    if wait:
        code = proc.wait()
        if code:
            raise ProcessError(code)
    else:
        try:
            proc.kill()
        except OSError:
            pass


if __name__ == '__main__':
    from sys import argv
    launch = (
        SystemLaunch()
        if os.path.basename(argv[0]).startswith('system') else
        SubprocessLaunch()
    )

    status = launch(argv[1:])
    print status
    raise SystemExit(status)
