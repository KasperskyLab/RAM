#!/usr/bin/python

from ram.classes.module import UnitService
from ram.classes.module import UseFilename
from ram.classes import LineResults


class __api__(UnitService):
    """shows description for the unit

  To see description for the unit:

    $ ram about <namepath>

    """

    _wrapper = UseFilename('about')

    _results = LineResults

    def __call__(self, ctx, *args, **kwargs):
        _short = kwargs.pop('short', False)

        if ctx.filename:
            lines = open(ctx.filename).read()
        else:
            lines = ""

        if _short and lines:
            return lines.splitlines().pop(0)
        else:
            return lines
