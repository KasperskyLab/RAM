#!/usr/bin/python

import gdbm
import fcntl


# hack to set gdbm.error to stringify its messages
# in conformance to IOError as its done in python3
def stringify_gdbm_error(self):
    return IOError(*self.args).__str__()

setattr(gdbm.error, '__str__', stringify_gdbm_error)

error = gdbm.error


from . import ConfigDict


class _DbmConfig(ConfigDict):
    def __init__(self, dirname, section, readonly):
        self.filename = dirname
        super(_DbmConfig, self).__init__(readonly=readonly, delblank=True, baresync=True)

    def __read__(self):
        try:
            if self.filename:
                return dict(gdbm.open(self.filename, 'r' if self.readonly else 'c'))
            else:
                raise gdbm.error()
        except gdbm.error:
            if self.readonly or not self.filename:
                return dict()
            else:
                raise

    def __sync__(self):
        if self.filename:
            db = gdbm.open(self.filename, 'n')
            for key in self:
                db[key] = self[key]
            db.close()


class _LockedDbmConfig(_DbmConfig):
    def __init__(self, dirname, section, readonly, lockname=None):
        self.lockfile = None
        if not readonly and lockname:
            self.lockfile = open(lockname, 'w', 0)
            fcntl.lockf(self.lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        super(_LockedDbmConfig, self).__init__(dirname, section, readonly)

    def __del__(self):
        if self.lockfile and fcntl:
            fcntl.lockf(self.lockfile, fcntl.LOCK_UN)
            self.lockfile.close()


from . import configopen


cfgopen = configopen(_LockedDbmConfig)
