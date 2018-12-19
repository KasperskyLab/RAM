#!/usr/bin/python

from ram.classes.module import UnitService
from ram.classes.module import UseLocation
from ram.classes import ReprResults


class __api__(UnitService):
    """(experimental) use python to import namepath
    """

    _wrapper = UseLocation()

    _results = ReprResults

    def __call__(self, location, *args, **kwargs):
        return __import__('ram.unitlib.' + str(location), fromlist=['*'])
