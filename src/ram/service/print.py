#!/usr/bin/python

from ram.classes.module import UnitService
from ram.classes.module import UseLocation
from ram.classes import ListResults

import ram


class __api__(UnitService):
    """prints selected configuration values

  To print configuration values for the unit:

    $ ram print <namepath> [<key>] ...

    """

    _wrapper = UseLocation()

    _results = ListResults

    def __call__(self, location, *args, **kwargs):
        if not args:
            return str(ram.query(str(location))).splitlines()
        else:
            return ram.value(str(location), *args)
