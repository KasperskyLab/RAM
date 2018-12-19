#!/usr/bin/python

from ram.classes import Service
from ram.classes import LineResults

from ram import service

from ram import __version__, __release__


class __api__(Service):
    """shows usage messages

  To see list of available services:

    $ ram proto

  To see help for a service:

    $ ram usage <service>

  To see list of all indexed units:

    $ ram index

    """

    _results = LineResults

    def __call__(self, *args, **kwargs):
        if args:
            srvname = args[0]
            srv_api = service[srvname]

            return srv_api.__doc__
        else:
            title = "the ram framework %(version)s" % {'version': __version__}
            lines = self.__doc__.splitlines()[1:]

            return "\n".join([title] + lines)
