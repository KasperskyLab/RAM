#!/usr/bin/python

from math import log10

import ram.widgets

from utils import ValidateIntRangeOrZero, BuildBytes, ParseBytes


def _BuildByteSize(_num, _pow, zero=None, digits=False):
    if zero is None:
        zero = "0"

    size = _num * (10 ** (_pow-1))

    if not _pow:
        return zero
    elif digits:
        return str(size)
    else:
        return BuildBytes(size, precise=-3, bsuffix=True)


def _ParseByteSize(_str, _def):
    try:
        size = int(_str)
    except ValueError:
        size = 0

    _low = int(log10(_def))
    _pow = len(_str.lstrip('+-')) if size else 0
    _pow = _pow - _low if _pow > _low else 0
    _num = size / (10 ** (_pow-1)) if _pow else _def

    return _num, _pow


class ByteSizeEntry(object):

    def __init__(self, header, text, title, size_str, size_def=1, n_orders=1, zero=None):
        self.header = header
        self.text = text
        self.title = title
        self.size_def, self.n_orders = size_def, n_orders
        self.size_num, self.size_pow = _ParseByteSize(size_str, size_def)
        self.zero = zero

    def validate(self, value):
        try:
            filesize = ParseBytes(value, rounded=True, bsuffix=True)
        except Exception as e:
            raise ValueError("incorrect value")
        return ValidateIntRangeOrZero(
            filesize, rangemin=self.size_def,
            rangemax=self.size_def * (10 ** (self.n_orders - 1)) - 1
        )

    def __call__(self, action):
        if action == ram.widgets.ACTION_SET:
            _filesize, = ram.widgets.RunEntry(
                self.header,
                self.text,
                [
                    (
                        self.title,
                        _BuildByteSize(self.size_num, self.size_pow),
                        self.validate
                    ),
                ]
            )
            self.size_num, self.size_pow = _ParseByteSize(
                str(ParseBytes(_filesize, rounded=True, bsuffix=True)),
                self.size_def
            )
        elif action == ram.widgets.ACTION_DEC:
            self.size_pow = (self.size_pow - 1) % self.n_orders
        elif action == ram.widgets.ACTION_INC:
            self.size_pow = (self.size_pow + 1) % self.n_orders

    def __str__(self):
        return _BuildByteSize(self.size_num, self.size_pow, self.zero)

    def __repr__(self):
        return _BuildByteSize(self.size_num, self.size_pow, digits=True)
