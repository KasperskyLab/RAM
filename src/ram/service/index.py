#!/usr/bin/python

from ram.classes import Service
from ram.classes import DictResults

import ram.locator

import ram


class LocatorInfo(object):
    def __init__(self, locator):
        self.locator = locator

    def _about(self):
        return ram.about(str(self.locator), short=True)

    def _entry(self, entry, marked):
        return marked if self.locator['%s' % entry, '%s.*' % entry] else "-"

    def _proto(self):
        return "".join(self._entry(entry, marked) for (marked, entry) in (
            ("*", 'input'),
            (".", 'query'),
            (".", 'store'),
            (".", 'apply'),
        ))

    def __str__(self):
        return "%s %s" % (
            self._proto(),
            self._about(),
        )


class __api__(Service):
    """shows list of indexed units

  To see list of all indexed units:

    $ ram index

  To see list of all units at namepath:

    $ ram index <namepath>

    """
    _results = DictResults

    def __call__(self, *args, **kwargs):
        nameroot = ram.locator(args[0]).split('.') if args else []

        return dict(
            (namepath, LocatorInfo(ram.locator[namepath]))
            for namepath in ram.locator
            if (namepath.split('.')[:-1] == nameroot)
        )
