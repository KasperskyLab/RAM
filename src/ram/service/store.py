#!/usr/bin/python

from ram.classes.module import UnitService
from ram.classes.module import UseMultiple
from ram.classes import ReprResults

import ram.symbols


class __api__(UnitService):
    """stores configuration to files

  To store configuration for the unit:

    $ ram store <namepath>

    """

    _wrapper = UseMultiple('store')

    _results = ReprResults

    def _service(self, *args, **kwargs):
        _input = kwargs.pop('input', None)
        _input = str(ram.symbols(_input))

        UnitService._service(self, *args, input=_input, **kwargs)

    def __call__(self, ctx, *args, **kwargs):
        _input = kwargs['input']

        if ctx.filename:
            return ram.symbols.proc(ctx.filename, *args, input=_input, environ=ctx._environ())
        else:
            return ram.symbols()
