#!/usr/bin/python

from glob import iglob

from ram.classes.module import UnitService
from ram.classes.module import UseFilename
from ram.classes import ListResults


class __api__(UnitService):
    """shows file list managed by the unit

  To see file list for the unit:

    $ ram files <namepath>

    """

    _wrapper = UseFilename('files')

    _results = ListResults

    def _lsfiles(self, *globs):
        for _glob in globs:
            for fpath in iglob(_glob.strip()):
                yield fpath

    def __call__(self, ctx, *args, **kwargs):
        if ctx.filename:
            globs = open(ctx.filename).read().splitlines()
        else:
            globs = []

        return list(self._lsfiles(*globs))
