#!/usr/bin/python

from ram.formats.ini import cfgopen

from collections import MutableMapping


# Cannot subclass bool. Use str with empty and non-empty values.
class Option(str):
    def __new__(self, value=None):
        if value is None:
            raise TypeError("Cannot use `None` as option value.")
        elif value in ['yes', 'y', 'on', 'true']:
            value = "_"
        elif value in ['no', 'n', 'off', 'false']:
            value = ""
        elif isinstance(value, basestring):
            raise TypeError("Cannot convert string `%s` to option value." % value)
        else:
            value = "_" if value else ""

        return str.__new__(self, value)

    def __str__(self):
        return 'yes' if self else 'no'


class Options(MutableMapping):
    _default = {
        'apply': False,     # run apply after successful setup
        'debug': False,     # show tracebacks for ram exceptions
        'errpt': False,     # force to use stderr as widgets io
        'local': False,     # allow to open units by local path
        'shell': False,     # use system in favour of subprocess
        'trace': False,     # trace unit subprocesses
    }

    def __init__(self):
        self.options = {}

    def __getitem__(self, key):
        if not key in self._default:
            raise KeyError("Cannot get option with name `%s`." % key)
        try:
            return self.options[key]
        except KeyError:
            return Option(self._default[key])

    def __setitem__(self, key, value):
        if value is None:
            del self[key]
        elif not key in self._default:
            raise KeyError("Cannot set option with name `%s`." % key)
        else:
            self.options[key] = Option(value)

    def __delitem__(self, key):
        if not key in self._default:
            raise KeyError("Cannot reset option with name `%s`." % key)
        try:
            del self.options[key]
        except KeyError:
            pass

    def __iter__(self):
        return iter(self._default)

    def __len__(self):
        return len(self._default)


def _query():
    options = Options()
    persist = cfgopen('/etc/ram/ram.conf', 'defaults', True, createns=True)

    for key in persist:
        options[key] = persist[key]

    return options


def _store(options):
    default = Options()
    persist = cfgopen('/etc/ram/ram.conf', 'defaults', False, createns=True)

    for key, value in options.iteritems():
        p_value = persist[key]
        if p_value:
            p_value = Option(p_value)
        else:
            p_value = default[key]

        if p_value != value:
            persist[key] = value

    persist.sync()


from contextlib import contextmanager


class __api__(object):

    _options = _query()

    def __getitem__(self, key):
        return self._options[key]

    @contextmanager
    def __call__(self):
        options = _query()
        yield options
        _store(options)
