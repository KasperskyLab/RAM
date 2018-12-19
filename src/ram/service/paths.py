#!/usr/bin/python

from ram.classes import Service
from ram.classes import ListResults

from ram.library import PathControl


class __api__(Service):
    """shows or edits library search paths

  To see list of library search paths:

    $ ram paths

  To assign colon-separated list to library search paths:

    $ ram paths assign <path>[:<path>...]

  To insert path to library search paths:

    $ ram paths insert <path>

  To remove path from library search paths:

    $ ram paths remove <path>

    """

    _results = ListResults

    def _pathctl(self, action, pvalue):
        _library = PathControl()

        _subcmds = {
            'assign': _library.assign,
            'insert': _library.insert,
            'remove': _library.remove,
        }

        if action:
            try:
                _subcmds[action](pvalue)
            except KeyError:
                raise RuntimeError("Unknown subcommand: `%s`." % action)

        for path in _library:
            yield path

    def __call__(self, *args, **kwargs):
        try:
            action = args[0]
        except IndexError:
            action = None

        try:
            pvalue = args[1]
        except IndexError:
            pvalue = None

        return list(self._pathctl(action, pvalue))
