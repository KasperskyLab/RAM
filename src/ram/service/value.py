#!/usr/bin/python

from __future__ import print_function

from ram.classes.module import UnitService
from ram.classes.module import UseLocation
from ram.classes import ListResults

import ram


class __api__(UnitService):
    """returns selected configuration values

  To print configuration values for the unit:

    $ ram value <namepath> [<key>] ...

    """

    _wrapper = UseLocation()

    _results = ListResults

    def _symbols(self, symbols, args):
        for _ in args:
            value = symbols[_]
            if isinstance(value, basestring):
                yield value
            else:
                yield ""

    def __call__(self, location, *args, **kwargs):
        symbols = ram.query(str(location))

        return iter(self._symbols(symbols, args))
