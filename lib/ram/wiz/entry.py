#!/usr/bin/python

from entry_iterable import RunDictEntry

from entry_iterable import RunListEntry

from entry_iterable import RunDictIndex

from entry_bytesize import ByteSizeEntry


import ram
from ram.process import ProcessError


def UnitEntry(namepath, *args, **kwargs):
    input = kwargs.pop('input', True)
    apply = kwargs.pop('apply', True)
    pause = kwargs.pop('pause', True)

    def __fn_unit(namepath=namepath, args=args, pause=pause, apply=apply, input=input):
        try:
            mode = 'input'
            if input:
                ram.input(namepath, *args)
            mode = 'apply'
            if apply:
                ram.apply(namepath)
        except ProcessError as e:
            print
            print "Error at:"
            print "\t%s: %s" % (mode, namepath)
            print "\tparam: %s" % ' '.join(args)
            print
            if pause:
                print "Press ENTER to continue ..."
                raw_input()
            else:
                raise SystemExit(*e.args)

    return __fn_unit


def InputUnitEntry(namepath, *args, **kwargs):
    kwargs['input'] = True
    kwargs['apply'] = False

    return UnitEntry(namepath, *args, **kwargs)


def ApplyUnitEntry(namepath, *args, **kwargs):
    kwargs['input'] = False
    kwargs['apply'] = True

    return UnitEntry(namepath, *args, **kwargs)
