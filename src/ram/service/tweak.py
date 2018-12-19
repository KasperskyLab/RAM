#!/usr/bin/python

from ram.classes import Service
from ram.classes import ListResults

import ram.options


class __api__(Service):
    """shows or edits internal parameters

  To see list of all internal parameters:

    $ ram tweak

  To see value of the given parameter:

    $ ram tweak <parameter>

  To change value of the parameter:

    $ ram tweak <parameter> <value>

    """

    _results = ListResults

    def _options(self, option, ovalue):
        with ram.options() as options:
            if option is None:
                for _option, _ovalue in options.iteritems():
                    yield "%s=%s" % (_option, _ovalue)
            else:
                if ovalue is not None:
                    options[option] = ovalue

                yield "%s=%s" % (option, options[option])

    def __call__(self, *args, **kwargs):
        try:
            option = args[0]
        except IndexError:
            option = None

        try:
            ovalue = args[1]
        except IndexError:
            ovalue = None

        return list(self._options(option, ovalue))
