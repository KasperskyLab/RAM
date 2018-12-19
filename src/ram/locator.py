#!/usr/bin/python


import ram.library


class Locator(object):

    def __init__(self, namepath, rootpath=None):
        if not namepath:
            raise LookupError("namepath cannot be empty.")

        if rootpath:
            self.namepath = rootpath + '.' + namepath
        else:
            self.namepath = namepath

    def __nonzero__(self):
        return bool(ram.library.check_dirs(self.namepath))

    def __iter__(self):
        return iter(self[...])

    def __str__(self):
        return self.namepath

    def __getitem__(self, wildcard):
        if not self:
            raise LookupError("No unit found: `%s`." % self.namepath)

        entries = {}

        for _subname, _subpath in ram.library.scan_paths(self.namepath, wildcard).items():
            if _subpath:
                location = _subpath
            elif not '.' in _subname:
                location = Locator(_subname, self.namepath)
            else:
                continue

            entries[_subname] = location

        if isinstance(wildcard, slice):
            raise NotImplementedError()
        elif not isinstance(wildcard, basestring):
            return entries
        elif wildcard in entries:
            return entries[wildcard]
        else:
            raise LookupError("No `%s` file found for unit `%s`." % (wildcard, self.namepath))


class __api__(object):

    def _subdirs(self, namepath=None):
        for _subname in ram.library.find_files(namepath, files=False, dirs=True):
            _subpath = (namepath + '.' + _subname) if namepath else _subname
            yield _subpath

            for _subitem in self._subdirs(_subpath):
                yield _subitem

    def __iter__(self):
        for namepath in self._subdirs():
            yield namepath

    def __getitem__(self, namepath):
        return Locator(namepath)

    def __call__(self, namepath=None, extended=False):
        namepath = ram.library._namepath(namepath)
        specific = ram.library._specific()

        if extended:
            return namepath, specific
        else:
            return namepath
