#!/usr/bin/python

import sys

import ram

import ram.locator
from ram.storage import Storage


class System(object):
    @staticmethod
    def OsFlavor():
        return ram.query('sys.distrib')['base']


def Params():
    return ram.param()


def Config(namepath=None):
    if namepath:
        namepath = ram.locator(namepath)

    try:
        thisunit = ram.locator()
        readonly = thisunit != namepath
    except LookupError:
        readonly = True

    return Storage.conf(namepath)


def Locate(name, namepath=None):
    return ram.which(namepath)[name]


def Notify(msgs):
    print msgs


def Failed(msg=None):
    raise SystemExit(msg or '')


def Report(status):
    raise SystemExit(0 if status else 1)


# ---- unit import ----
from pkgutil import ImpLoader, ModuleType
from ram.context import LocatorFinder


__path__ = []

_modules = {}
_configs = {}


class UnitLibModule(ModuleType):
    def __new__(self, module, config):
        self = module.__class__.__new__(self, module.__name__)
        for attr in module.__dict__:
            setattr(self, attr, getattr(module, attr))

        _modules[self] = module
        _configs[self] = config

        return self

    def __init__(self, module, config):
        pass

    def __getitem__(self, key):
        return _configs[self][key]

    def __setitem__(self, key, value):
        _configs[self][key] = value

    def __delitem__(self, key):
        del _configs[self][key]

    def __iter__(self):
        return iter(_configs[self].keys())

    def __len__(self):
        return len(_configs[self].keys())

    def keys(self):
        return _configs[self].keys()

    def iterkeys(self):
        return _configs[self].iterkeys()

    def values(self):
        return _configs[self].values()

    def itervalues(self):
        return _configs[self].itervalues()

    def items(self):
        return _configs[self].items()

    def iteritems(self):
        return _configs[self].iteritems()

    def __getattribute__(self, name):
        try:
            if name == '__class__':
                raise AttributeError()
            return object.__getattribute__(self, name)
        except AttributeError:
            return object.__getattribute__(_modules[self], name)


class LocatorLoader(ImpLoader):
    def load_module(self, fullname):
        module = ImpLoader.load_module(self, fullname)
        if not isinstance(module, UnitLibModule):
            config = ram.query(self.fullname)
            module = UnitLibModule(module, config)
        if not hasattr(module, '__path__'):
            setattr(module, '__path__', [])
        sys.modules[fullname] = module
        return module


sys.meta_path.insert(0, LocatorFinder(__name__, LocatorLoader))
