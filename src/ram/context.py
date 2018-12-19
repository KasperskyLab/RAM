#!/usr/bin/python

import imp

from contextlib import contextmanager

import ram.library


class __api__(object):
    _saved_import = None
    _context_dict = {}

    @staticmethod
    def _imp_namepath(namebase, namerest, globals=None, locals=None, fromlist=None):
        basename = 'ram.unitlib.%s' % '.'.join(namebase + namerest[:1])
        fullname = 'ram.unitlib.%s' % '.'.join(namebase + namerest)

        imported = __api__._saved_import(fullname, globals, locals, fromlist, 0)
        toplevel = __api__._saved_import(basename, globals, locals, ['__name__'], 0)

        if imported is None or fromlist:
            return imported
        else:
            return toplevel

    @staticmethod
    def _rel_namebase(level):
        try:
            namepath = ram.library._namepath(None)
            namebase = namepath.split('.')

            haslevel = abs(level)
            if not haslevel:
                raise LookupError()

            cutlevel = haslevel-1
            if len(namebase) < cutlevel:
                return __api__._saved_import('', {'__package__': namepath}, None, None, level=cutlevel)

            return namebase[:-cutlevel or None]
        except LookupError:
            return None

    @staticmethod
    def _get_location(namepath):
        nameroot, _, name = namepath.rpartition('.')

        try:
            return imp.find_module(name, list(ram.library._pathlist(nameroot)))
        except ImportError:
            if not ram.library.check_dirs(namepath):
                raise

            # virtual packages
            return None, namepath, ('', '', imp.PKG_DIRECTORY)

    @staticmethod
    def _has_toplevel(namebase, namerest):
        try:
            return __api__._get_location('.'.join(namebase + namerest[:1]))
        except ImportError:
            return None

    @staticmethod
    def _units_import(name, globals=None, locals=None, fromlist=None, level=-1):
        importto = globals and globals.get('__name__')
        if importto in __api__._context_dict:
            namerest = name.split('.') if name else []

            rellevel = level if importto == '__main__' else 0
            namebase = __api__._rel_namebase(rellevel)

            if namebase is not None and (__api__._has_toplevel(namebase, namerest) or rellevel > 0):
                return __api__._imp_namepath(namebase, namerest, globals, locals, fromlist)

            namebase = []
            if __api__._has_toplevel(namebase, namerest) and level <= 0:
                return __api__._imp_namepath(namebase, namerest, globals, locals, fromlist)

        return __api__._saved_import(name, globals, locals, fromlist, level)

    @contextmanager
    def __call__(self, name):
        __api__._context_dict.setdefault(name, 0)
        __api__._context_dict[name] += 1

        try:
            yield name
        finally:
            __api__._context_dict[name] -= 1
            if not __api__._context_dict[name]:
                del __api__._context_dict[name]


class LocatorFinder(object):
    def __init__(self, name, loader):
        self.name = name + '.'
        self.loader = loader

    def find_module(self, fullname, path=None):
        if not fullname.startswith(self.name):
            return None

        namepath = fullname[len(self.name):]
        location = __api__._get_location(namepath)

        try:
            return self.loader(namepath, *location)
        except ImportError:
            return None


import __builtin__

__api__._saved_import = __builtin__.__import__
__builtin__.__import__ = __api__._units_import
