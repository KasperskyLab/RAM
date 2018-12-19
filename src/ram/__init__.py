#!/usr/bin/python

import sys

from pkgutil import ImpLoader, ImpImporter, ModuleType


__version__ = '0.4.9'
__release__ = ''


class _RamModule(ModuleType):
    _classes = {}
    _modapis = {}
    _modules = {}

    def __new__(self, module, modapi):
        self = module.__class__.__new__(self, module.__name__)
        self.__class__ =  type('_module', (_RamModule, modapi.__class__), {})

        for name in dir(module):
            try:
                setattr(self, name, getattr(module, name))
            except (TypeError, AttributeError) as e:
                pass

        _RamModule._modules[self] = module

        for name in dir(modapi):
            try:
                setattr(self, name, getattr(modapi, name))
            except (TypeError, AttributeError) as e:
                pass

        _RamModule._modapis[self] = modapi

        return self

    def __init__(self, module, objapi):
        pass

    def __getattribute__(self, name):
        if name == '__class__':
            return _RamModule._classes[self]

        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            pass

        try:
            return object.__getattribute__(_RamModule._modapis[self], name)
        except AttributeError:
            return object.__getattribute__(_RamModule._modules[self], name)


import imp


class _RamLoader(ImpLoader):
    def load_module(self, fullname):
        module = ImpLoader.load_module(self, fullname)
        if hasattr(module, '__api__'):
            sys.modules[fullname] = _RamModule(module, module.__api__())
        else:
            sys.modules[fullname] = module
        return sys.modules[fullname]


class _RamFinder(object):
    def __init__(self, name):
        self.name = name + '.'

    def find_module(self, fullname, path=None):
        if not fullname.startswith(self.name):
            return

        namepath, _, name = fullname.rpartition('.')

        try:
            file, filename, etc = imp.find_module(name, path)
        except ImportError:
            return None

        return _RamLoader(fullname, file, filename, etc)


sys.meta_path.insert(0, _RamFinder(__name__))


import ram.service


class __api__(object):

    class ServiceCall(object):
        def __init__(self, srvname):
            self.srvname = srvname

        def __call__(self, *args, **kwargs):
            service = ram.service[self.srvname]
            return service._service(*args, **kwargs)

    class ServiceIter(object):
        def __init__(self, srvname):
            self.srvname = srvname

        def __call__(self, *args, **kwargs):
            service = ram.service[self.srvname]
            return service._iterate(*args, **kwargs)

    for srvname in ram.service:
        srvcall = srvname
        srviter = '_' + srvname
        locals()[srvcall] = ServiceCall(srvname)
        locals()[srviter] = ServiceIter(srvname)

    def __call__(self, srvname, *args, **kwargs):
        return ram.service[srvname]._service(*args, **kwargs)


sys.modules[__name__] = _RamModule(sys.modules[__name__], __api__())
