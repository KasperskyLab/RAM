#!/usr/bin/python

from ram.classes import Service
from ram.classes import DictResults

from ram import service


class ServiceInfo(object):
    def __init__(self, srv_api=None, srv_ctx=None, srv_err=None):
        self.srv_api = srv_api
        self.srv_err = srv_err

    def __str__docstr(self):
        if self.srv_err:
            return "%s: %s" % (
                self.srv_err.__class__.__name__,
                self.srv_err
            )
        elif self.srv_api.__doc__:
            return self.srv_api.__doc__.splitlines().pop(0)
        else:
            return ""

    def __str__marked(self):
        if self.srv_err:
            return "!"
        elif self.srv_api:
            return "*"
        else:
            return " "

    def __str__(self):
        return "%s %s" % (
            self.__str__marked(),
            self.__str__docstr(),
        )


class __api__(Service):
    """shows list of available services

  To see list of available services:

    $ ram proto

    """

    _results = DictResults

    defaults = {
        'width': 15,
    }

    def _lsproto(self):
        for srvname in service:
            try:
                srv_api = service[srvname]
                yield srvname, ServiceInfo(srv_api)
            except Exception as err:
                yield srvname, ServiceInfo(srv_err=err)

    def __call__(self, *args, **kwargs):
        return dict(self._lsproto())
