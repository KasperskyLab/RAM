#!/usr/bin/python

import cPickle as pickle

from ram.classes.module import UnitService
from ram.classes.module import UseFilename
from ram.classes import DumbResults

import ram.process

from ram.osutils import setenv


class __api__(UnitService):
    """runs dialogs to interact with user

  To run dialogs for the unit:

    $ ram input <namepath> [<param>] ...

    """

    _wrapper = UseFilename('input', required=True)

    _results = DumbResults

    def __call__(self, ctx, *args, **kwargs):
        setenv('RAMARGS', pickle.dumps(args))

        if ctx.filename:
            ram.process.invoke(ctx.filename, *args, environ=ctx._environ())
