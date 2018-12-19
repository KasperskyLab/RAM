#!/usr/bin/python


import os

from glob import iglob

import ram.osutils


pathfile = '/etc/ram/location.list'


class PathControl(object):
    def __iter__(self):
        try:
            for path in filter(bool, ram.osutils.getenv('RAMPATH').split(':')):
                yield path
            for path in filter(bool, map(str.strip, open(pathfile).readlines())):
                yield path
        except IOError:
            pass

    def assign(self, pathlist=None):
        if pathlist is None:
            raise ValueError("Cannot set library paths to `%s`." % pathlist)
        elif isinstance(pathlist, basestring):
            pathlist = pathlist.split(':') if pathlist else []

        with ram.osutils.safe_tempfile(pathfile) as tempfile:
            tempfile.writelines("%s\n" % _ for _ in pathlist)

    def insert(self, path=None):
        if not path:
            raise ValueError("Cannot insert empty path.")

        pathlist = filter(bool, map(str.strip, open(pathfile).readlines()))
        pathlist.insert(0, path)

        return self.assign(pathlist)

    def remove(self, path=None):
        if not path:
            raise ValueError("Cannot remove empty path.")

        pathlist = filter(bool, map(str.strip, open(pathfile).readlines()))
        if not path in pathlist:
            return
        pathlist.remove(path)

        return self.assign(pathlist)


def _pathlist(namepath=None):
    namelist = namepath.split('.') if namepath else []
    if not all(namelist):
        raise ValueError("Incorrect namepath value: `%s`" % namepath)
    for path in sorted(set(PathControl())):
        yield os.path.join(path, *namelist)


def _namepath(namepath):
    if namepath is None:
        namepath = '.'
    elif namepath == '-':
        namepath = '.'
    elif not isinstance(namepath, basestring):
        namepath = namepath.__file__

    thisunit = ram.osutils.getenv('RAMUNIT')
    if not namepath and not thisunit:
        return namepath
    elif not namepath:
        namepath = '.'

    splitted = namepath.split('.')
    if splitted and not splitted[-1]:
        splitted.pop()

    complete = []
    for expanded, pathitem in enumerate(splitted):
        if pathitem:
            complete.append(pathitem)
        elif complete:
            complete.pop()
        elif expanded:
            break
        elif thisunit:
            complete.extend(thisunit.split('.'))
        else:
            break

    if not complete:
        raise LookupError("Failed to resolve namepath: `%s`." % namepath)

    return '.'.join(complete)


def _specific():
    specific = ram.osutils.getenv('RAMSPEC')
    if not specific:
        return None
    elif specific[0] == '/':
        return specific[1:]
    else:
        raise ValueError("Incorrect specific value: `%s`." % specific)


def check_dirs(namepath):
    return ram.osutils.check_dirs(_pathlist(namepath))


def scan_paths(namepath, wildcard):
    return ram.osutils.scan_paths(_pathlist(namepath), wildcard)


def find_files(namepath, *args, **kwargs):
    return ram.osutils.find_files(_pathlist(namepath), *args, **kwargs)


if __name__ == '__main__':
    ram.osutils.setenv('RAMUNIT', 'xxxx.y.zzz')

    def _test_namepath(namepath, shouldbe):
        try:
            resolved = _namepath(namepath)
        except LookupError as err:
            print str(err)
            resolved = None

        _correct = ' ' if resolved == shouldbe else '!'

        print "%1s %-16s %-16s %-16s" % (_correct, namepath, resolved, shouldbe)

    _test_namepath(os, '')
    _test_namepath('', 'xxxx.y.zzz')
    _test_namepath('.', 'xxxx.y.zzz')
    _test_namepath('-', 'xxxx.y.zzz')
    _test_namepath(None, 'xxxx.y.zzz')
    _test_namepath('.ww', 'xxxx.y.zzz.ww')
    _test_namepath('.w.w', 'xxxx.y.zzz.w.w')
    _test_namepath('..', 'xxxx.y')
    _test_namepath('..qqq', 'xxxx.y.qqq')
    _test_namepath('.ww..', 'xxxx.y.zzz')
    _test_namepath('.ww..ww', 'xxxx.y.zzz.ww')
    _test_namepath('...', 'xxxx')
    _test_namepath('....', None)
    _test_namepath('.....', None)
