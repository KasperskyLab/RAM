#!/usr/bin/python

import pkgutil

from ram.classes import Service


class __api__(object):
    def __iter__(self):
        for _, srvname, _ in pkgutil.iter_modules(__path__):
            yield srvname

    def __getitem__(self, srvname):
        if not srvname:
            raise ImportError("Service name cannot be empty.")
        srvpath = __name__ + '.' + srvname
        service = __import__(srvpath, fromlist=['__api__'])
        if not isinstance(service, Service):
            raise ImportError("No service interface found.")
        else:
            return service
