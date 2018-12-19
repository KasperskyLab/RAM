#!/usr/bin/python

from ram.classes.module import UnitService
from ram.classes.module import UseLocation
from ram.classes import DictResults


class __api__(UnitService):
    """shows file paths of unit files

  To see paths for all files of the unit:

    $ ram which <namepath>

  To see paths for files matched the wildcard:

    $ ram which <namepath> <shell-wildcard>

  To see paths for files matched any of wildcards:

    $ ram which <namepath> <shell-wildcard> <shell-wildcard> ...

    """

    _results = DictResults

    _wrapper = UseLocation()

    defaults = {
        'names': False,
    }

    def __call__(self, location, *args, **kwargs):
        entries = location[args or None]

        return dict(
            (k, v) for (k, v) in entries.iteritems()
            if isinstance(v, basestring)
        )
