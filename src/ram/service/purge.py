#!/usr/bin/python

from ram.classes.module import UnitService
from ram.classes.module import UseLocation
from ram.classes import DumbResults


class __api__(UnitService):
    """(deprecated) only for compatibility
    """

    _wrapper = UseLocation()

    _results = DumbResults

    def __call__(self, location, *args, **kwargs):
        pass
