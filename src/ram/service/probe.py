#!/usr/bin/python

from ram.classes.module import UnitService
from ram.classes.module import UseMultiple
from ram.classes import DumbResults

import ram.process


class __api__(UnitService):
    """probes service in the environment

  To probe service of the unit:

    $ ram probe <namepath>

    """

    _wrapper = UseMultiple('probe')

    _results = DumbResults

    def __call__(self, ctx, *args, **kwargs):
        if ctx.filename:
            ram.process.invoke(ctx.filename, *args, environ=ctx._environ())
