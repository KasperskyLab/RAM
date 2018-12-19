#!/usr/bin/python

from ram.classes.module import UnitService
from ram.classes.module import UseFilename
from ram.classes import IterResults

from ram.watches import track_output


class __api__(UnitService):
    """watches events sensible for the unit

  To watch events for the unit:

    $ ram watch <namepath>

    """

    _wrapper = UseFilename('watch', required=True)

    _results = IterResults

    def __call__(self, ctx, *args, **kwargs):
        if ctx.filename:
            return track_output(ctx.filename, *args)
        else:
            return iter(())
