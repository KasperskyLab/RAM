#!/usr/bin/python

from ram.classes.module import UnitService
from ram.classes.module import UseLocation
from ram.classes import DumbResults

import ram


class __api__(UnitService):
    """(deprecated) same as store service
    """

    _wrapper = UseLocation()

    _results = DumbResults

    def __call__(self, location, *args, **kwargs):
        return ram.store(str(location), *args, **kwargs)
