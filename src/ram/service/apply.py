#!/usr/bin/python

from ram.classes.module import UnitService
from ram.classes.module import UseMultiple
from ram.classes import DumbResults

import ram.process


class __api__(UnitService):
    """applies configuration to environment

  To apply configuration of the unit:

    $ ram apply <namepath>

    """

    _wrapper = UseMultiple('apply')

    _results = DumbResults

    def __call__(self, ctx, *args, **kwargs):
        if ctx.filename:
            ram.process.invoke(ctx.filename, *args, environ=ctx._environ())
