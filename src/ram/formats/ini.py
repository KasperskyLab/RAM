#!/usr/bin/python

import iniparse

from ram.osutils import TrySubmit

# hack to force iniparse to return empty string for non-present keys.
setattr(iniparse.config, 'Undefined', lambda name, namespace: '')

from . import SyncedDict


class _IniConfig(SyncedDict):
    def __init__(self, dirname, section, readonly, delblank=False, createns=False):
        self.filename = dirname
        self.section  = section
        self.createns = createns
        try:
            self.ini_conf = iniparse.INIConfig(open(self.filename))
        except IOError:
            self.ini_conf = iniparse.INIConfig()

        super(_IniConfig, self).__init__(readonly=readonly, delblank=delblank)

    def __read__(self):
        if not self.section in self.ini_conf._sections:
            if self.createns:
                self.ini_conf._new_namespace(self.section)
            else:
                raise IOError("Cannot find section `%s` in config file." % self.section)

        return self.ini_conf[self.section]

    def __sync__(self):
        if not TrySubmit(self.filename, [str(self.ini_conf)]):
            raise IOError("Failed to update `%s`." % self.filename)


from . import configopen


cfgopen = configopen(_IniConfig, mergepath=False)
