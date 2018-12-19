#!/usr/bin/python

from pipes import quote
from shlex import shlex
from string import ascii_letters, digits
from collections import OrderedDict

from ram.osutils import TryUnlink, TrySubmit, TouchFile


class ConfigParseError(Exception):
    pass


def ParseConfigurationLine(line):
    vars = OrderedDict()
    comment = ''
    while True:
        # remove empty or full-commented lines
        line = line.strip()
        if not line or line.startswith('#'):
            comment = line
            break

        # validate assigment syntax
        key, sep, value = line.partition('=')
        if not key or not sep:
            raise ConfigParseError("Non-assignment statement")

        # validate assignment syntax
        if key != key.rstrip():
            raise ConfigParseError("Spaces before assignment operator")

        # validate key is variable name
        if not key[0] in ascii_letters + '_':
            raise ConfigParseError("Bad character in variable name")

        if not all((c in ascii_letters + digits + '_') for c in key):
            raise ConfigParseError("Bad character in variable name")

        # parse value
        parse = shlex(value, posix=True)
        parse.commenters = ''
        parse.whitespace_split = True

        # Using shlex() is not a perfect solution. It deals reasonably
        # with simple configuration values and quoted/escaped strings.
        # But once input has shell punctuation characters it doesn't care.
        # Should be fixed with introduction of punctuation_chars in python 3.x.

        try:
            vars[key] = value == value.lstrip() and parse.get_token() or ''
        except ValueError as e:
            raise ConfigParseError(e)

        # continue to parse
        line = value[parse.instream.tell():]

    return vars, comment


from . import SyncedDict


class _EnvConfig(SyncedDict):
    def __init__(self, dirname, section=None, readonly=True, delempty=False, keeperrs=False, error_cb=None, delblank=True):
        self.delempty = delempty
        self.keeperrs = keeperrs
        self.filename = dirname
        self.error_cb = error_cb

        super(_EnvConfig, self).__init__(readonly=readonly, delblank=delblank)

    def __read__(self):
        try:
            self.cfglines = open(self.filename).readlines()
        except Exception as e:
            self.cfglines = []

        dict_obj = OrderedDict()
        for lnum, line in enumerate(self.cfglines):
            try:
                parsed, comment = ParseConfigurationLine(line)
                if parsed:
                    dict_obj.update(parsed)
            except ConfigParseError as e:
                if self.error_cb:
                    self.error_cb(self.filename, lnum, e)

        return dict_obj

    def __sync__(self):
        TouchFile(self.filename)

        newlines = []
        todump = {}
        for k, v in self.iteritems():
            todump[k] = '%s=%s' % (k, v and quote(v))

        for lnum, line in enumerate(self.cfglines):
            try:
                parsed, comment = ParseConfigurationLine(line)
            except ConfigParseError:
                newlines += [('' if self.keeperrs else '#') + line]
                continue

            picked = [todump.pop(_var) for _var in parsed if _var in todump]
            picked += [comment] if comment else []
            if not picked:
                continue

            newlines += [' '.join(picked) + '\n']

        for _var in todump.keys():
            newlines += [todump.pop(_var) + '\n']

        if not newlines and self.delempty:
            if not TryUnlink(self.filename):
                raise IOError("Failed to update `%s`." % self.filename)
        else:
            if not TrySubmit(self.filename, newlines):
                raise IOError("Failed to update `%s`." % self.filename)

        self.cfglines = newlines

from . import configopen

cfgopen = configopen(_EnvConfig, mergepath=True)
