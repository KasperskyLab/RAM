#!/usr/bin/python

from . import Service

import ram.locator


class CallContext(object):
    def __init__(self, location, filemode, filename):
        self.location = location
        self.filemode = filemode
        self.filename = filename

    def _environ(self):
        return dict(
            RAMUNIT=str(self.location),
            RAMMODE=str(self.filemode),
        )


class CallContextFactory(object):
    def __init__(self, location, filemode, required):
        self.location = location
        self.filemode = filemode
        self.required = required

    def __iter__(self):
        wildcard = self.filemode + '.*'
        for filename in self.location[wildcard,]:
            yield filename[len(self.filemode):]

    def __call__(self, specific=None):
        if specific is None:
            specific = ''

        try:
            filename = self.location[self.filemode + specific]
        except LookupError:
            if self.required:
                raise

            filename = None

        return CallContext(
            self.location,
            self.filemode,
            filename,
        )


class UseLocation(object):
    def __call__(self, location, callfunc):
        return callfunc(location)


class UseFilename(object):
    def __init__(self, filemode, required=False):
        self.filemode = filemode
        self.required = required

    def __call__(self, location, callfunc):
        cc_fac = CallContextFactory(
            location,
            self.filemode,
            self.required,
        )

        return callfunc(cc_fac())


class UseMultiple(UseFilename):
    def __call__(self, location, callfunc):
        cc_fac = CallContextFactory(
            location,
            self.filemode,
            self.required,
        )

        result = callfunc(cc_fac())

        failed = []

        for specific in cc_fac:
            try:
                callfunc(cc_fac(specific))
            except Exception as err:
                failed += [err]

        if failed:
            raise RuntimeError(len(failed))

        return result


class UnitService(Service):

    _wrapper = None

    def _service(self, *args, **kwargs):
        try:
            namepath = args[0]
            args = args[1:]
        except IndexError:
            namepath = None

        namepath = ram.locator(namepath)
        location = ram.locator[namepath]

        def callfunc(context, args=args, kwargs=kwargs):
            return Service._service(self, context, *args, **kwargs)

        return self._wrapper(location, callfunc)
