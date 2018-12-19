#!/usr/bin/python

from ram.classes.module import UnitService
from ram.classes.module import UseFilename
from ram.classes import ReprResults

import ram.symbols


class __api__(UnitService):
    """queries configuration from files

  To query configuration for the unit:

    $ ram query <namepath>

    """

    _wrapper = UseFilename('query')

    _results = ReprResults

    def __call__(self, ctx, *args, **kwargs):
        if ctx.filename:
            symbols = ram.symbols.proc(ctx.filename, *args, environ=ctx._environ())
        else:
            symbols = ram.symbols()

        if not args:
            return symbols
        else:
            results = ram.symbols()
            for arg in args:
                results[arg] = symbols[arg]
            return results
