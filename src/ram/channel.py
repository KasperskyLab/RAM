#!/usr/bin/python

import select

import socket

from ram.process import running_ps
from ram.osutils import getenv, setenv


def _channel_master(command, *args, **kwargs):
    _stdin = kwargs.pop('stdin', None)
    _input = kwargs.pop('input', None)
    _preexec = kwargs.pop('preexec', None)

    chan = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)

    def _preexec(chan=chan):
        s, c = chan

        s.close()
        setenv('RAMCHAN', str(c.fileno()))

    with running_ps(
        command, *args, stdin=True, wait=True,
        preexec=_preexec, **kwargs
    ) as proc:
        s, c = chan

        c.close()

        p = proc.stdin.fileno()

        fds_r = [s, p]
        fds_w = [s]

        while proc:
            got_r, got_w, _ = select.select(fds_r, fds_w, [])

            if s in got_w:
                if _input:
                    sent = s.send(_input)
                    _input = _input[sent:]
                else:
                    s.shutdown(socket.SHUT_WR)
                    fds_w.remove(s)

            elif s in got_r:
                data = s.recv(select.PIPE_BUF)
                if data:
                    yield data
                else:
                    s.shutdown(socket.SHUT_RD)
                    fds_r.remove(s)

            elif p in got_r:
                break

        s.close()


# channel api -- run background process and communicate with it via socket pair
# limitations
#   background process stdin is used to detect background process termination
#   background process shouldn't use daemonized forks in order to avoid locks
class __api__(object):
    def __call__(self, command, *args, **kwargs):
        return "".join(_channel_master(command, *args, **kwargs))


def _channel_slave(write):
    mode = 'w' if write else 'r'
    chan = int(getenv('RAMCHAN'))

    c = socket.fromfd(chan, socket.AF_UNIX, socket.SOCK_STREAM)
    return c.makefile(mode)


def _chan_wr():
    return _channel_slave(True)


def _chan_rd():
    return _channel_slave(False)
