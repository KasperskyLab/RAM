#!/usr/bin/python

import cPickle as pickle

from ram.classes.module import UnitService
from ram.classes.module import UseFilename
from ram.classes import ReprResults

from ram.osutils import getenv


class __api__(UnitService):
    """shows parameter list for the unit

  To see parameter list for the unit:

    $ ram param <namepath>

    """

    _wrapper = UseFilename('param')

    _results = ReprResults

    def __call__(self, ctx, *args, **kwargs):
        args = getenv('RAMARGS')
        args = pickle.loads(args) if args else ()

        if ctx.filename:
            lines = open(ctx.filename).read().splitlines()
        else:
            lines = []

        params = {}
        for _param in lines:
            key, sep, value = _param.partition('=')
            params[key] = value if sep else False

        for _param in args:
            key, sep, value = _param.partition('=')
            if key not in params:
                continue
            sep = str(params[key]) == params[key]
            params[key] = value if sep else True

        class Params(object):
            __slots__ = params

            def __init__(self, values):
                for key, value in values.iteritems():
                    setattr(self, key, value)

            def __iter__(self):
                for key in self.__slots__:
                    value = getattr(self, key)
                    if isinstance(value, basestring):
                        yield '%s=%s' % (key, value)
                    else:
                        yield '%s' % (key)

            def __str__(self):
                return '\n'.join(self)

        return Params(params)
