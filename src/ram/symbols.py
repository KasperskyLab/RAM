#!/usr/bin/python

from collections import Iterable, Mapping, MutableMapping


def build(*keys, **data):
    for key in sorted(data):
        value = data[key]
        local = list(keys) + [key]
        if isinstance(value, basestring):
            yield "%s=%s" % (".".join(local), value)
        else:
            for _ in build(*local, **value):
                yield _


def parse(lines):
    for lnum, line in enumerate(map(str.strip, lines)):
        if not line:
            continue
        key, _, value = line.partition('=')
        if not key or not _:
            raise ValueError("Parsing error on line %s: %s" % (lnum, line))
        else:
            yield key, value


class SymbolsProxy(str):
    def __new__(self, symbols):
        self = str.__new__(self)
        self.symbols = symbols
        return self

    def __setitem__(self, keypath, value):
        try:
            raise TypeError()
        except TypeError:
            return self.symbols.__setitem__(keypath, value)

    def __delitem__(self, keypath):
        try:
            raise TypeError()
        except TypeError:
            return self.symbols.__delitem__(keypath)

    def __getitem__(self, keypath):
        try:
            return str.__getitem__(self, keypath)
        except TypeError:
            return self.symbols.__getitem__(keypath)

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return object.__getattribute__(self.symbols, name)


class Symbols(MutableMapping, dict):
    def __init__(self, parent, parkey, *args, **kwargs):
        self.parent = None
        self.parkey = None

        self.update(*args, **kwargs)

        self.parent = parent
        self.parkey = parkey

    def __getitem__(self, keypath, private=False, keytest=False):
        if not private:
            parents, keypath = self._keyprepare(keypath, parents=False)

        keyhead = keypath.pop(0)
        symbols = dict.get(self, keyhead, Symbols(self, keyhead))
        if not symbols:
            symbols = SymbolsProxy(symbols)

        if keypath:
            if not isinstance(symbols, basestring):
                return symbols.__getitem__(keypath, private=True, keytest=keytest)
            elif not keytest:
                return symbols[keypath]
            else:
                return ""
        else:
            return symbols

    def __setitem__(self, keypath, value, private=False):
        if not private:
            if not isinstance(value, basestring) and not isinstance(value, Mapping) and not value is None:
                raise ValueError('Symbols can only contain strings or mappings, not `%s`' % (value,))

            if not value:
                return self.__delitem__(keypath)

            parents, keypath = self._keyprepare(keypath, parents=True)
            return parents.__setitem__(keypath, value, private=True)

        keyhead = keypath.pop(0)

        if keypath:
            symbols = dict.setdefault(self, keyhead, Symbols(self, keyhead))
            if not isinstance(symbols, basestring):
                return symbols.__setitem__(keypath, value, private=True)
            else:
                symbols[keypath] = value
                return

        if isinstance(value, Mapping):
            value = Symbols(self, keyhead, value)

        return dict.__setitem__(self, keyhead, value)


    def __delitem__(self, keypath, private=False):
        if not private:
            parents, keypath = self._keyprepare(keypath, parents=True)
            return parents.__delitem__(keypath, private=True)

        keyhead = keypath.pop(0)

        if keypath:
            symbols = dict.get(self, keyhead, Symbols(self, keyhead))
            if not isinstance(symbols, basestring):
                symbols.__delitem__(keypath, private=True)
            else:
                del symbols[keypath]
            if symbols:
                return

        if dict.__contains__(self, keyhead):
            dict.__delitem__(self, keyhead)


    def _keyprepare(self, keypath, parents=False):
        if isinstance(keypath, basestring):
            keylist = keypath.split('.') if keypath else []
        elif isinstance(keypath, Iterable):
            keylist = list(keypath)
        else:
            raise TypeError("Symbols can use only strings or sequences of strings as keys, not `%s`" % (keypath,))

        if not keylist or not all(keylist):
            raise TypeError("Symbols can use only non-empty keys and non-empty key elements, not `%s`" % (keypath,))

        for keyitem in keylist:
            if not all(c.isalnum() or c in ['_','-'] for c in keyitem):
                raise TypeError("Symbols can use only alnums, dash and underscore in key elements, not `%s`" % (keyitem,))

        symbols = self
        while parents and symbols.parkey:
            keylist.insert(0, symbols.parkey)
            symbols = symbols.parent

        return symbols, keylist

    def __contains__(self, keypath):
        return bool(self.__getitem__(keypath, keytest=True))

    def __iter__(self):
        return dict.__iter__(self)

    def __len__(self):
        return dict.__len__(self)

    def __str__(self):
        return "\n".join(build(**self))


import ram.channel


class __api__(object):
    def proc(self, *args, **kwargs):
        return self(ram.channel(*args, **kwargs))

    def send(self, symbols):
        ram.channel._chan_wr().write(str(symbols))

    def recv(self):
        return self(ram.channel._chan_rd().read())

    def __call__(self, _input=None):
        if _input is None:
            return Symbols(None, None)
        elif isinstance(_input, Mapping):
            return Symbols(None, None, _input)
        elif isinstance(_input, basestring):
            return Symbols(None, None, parse(_input.splitlines()))
        else:
            return Symbols(None, None, parse(_input.readlines()))
