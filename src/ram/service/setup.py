#!/usr/bin/python

from ram.classes.module import UnitService
from ram.classes.module import UseLocation
from ram.classes import DumbResults

import ram.options

_apply = ram.options['apply']



class __api__(UnitService):
    """(deprecated) same as input service

  To use unit:

    $ ram setup <namepath> [<param>] ...

    """

    _wrapper = UseLocation()

    _results = DumbResults

    def __call__(self, location, *args, **kwargs):
        ram.input(str(location), *args, **kwargs)
        if _apply:
            ram.apply(str(location))
