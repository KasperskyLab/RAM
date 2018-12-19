#!/usr/bin/python

from string import digits
from decimal import Decimal


def ValidateNonEmpty(value):
    if not value:
        raise ValueError("could not be empty")
    else:
        return value


def ValidateIntRange(value, rangemin=None, rangemax=None, allow_zero=False, banned=None):
    try:
        _value = int(value)
    except ValueError:
        raise ValueError("is not an integer")
    else:
        if banned and _value in banned:
            raise ValueError("is already used")
        if rangemin is None:
            rangemin = _value
        if rangemax is None:
            rangemax = _value
        if (not _value and allow_zero) or (rangemin <= _value <= rangemax):
            return value
        else:
            raise ValueError("is out of range")


def ValidateIntRangeOrZero(value, rangemin=None, rangemax=None, banned=None):
    return ValidateIntRange(value, rangemin, rangemax, allow_zero=True, banned=banned)


sizeunits = ["", "K", "M", "G", "T"]

# parted: bsuffix=False: K=KB=1000, Ki=KiB=1024
# ls, dd: bsuffix=True: KB=1000, K=1024


def BuildBytes(bytesize, precise=0, bsuffix=False):
    bytesize = int(bytesize)
    if not bytesize:
        return "0"

    power = int(Decimal(abs(bytesize)).log10() / 3)
    if not power < len(sizeunits):
        power = len(sizeunits) - 1

    sizeunit = sizeunits[power]
    sizebase = 1000 ** power
    sizemult = Decimal(bytesize) / sizebase

    sizemstr = str(sizemult.quantize(Decimal(10) ** -abs(precise)))
    sizemstr = sizemstr.rstrip('0').rstrip('.') if precise < 0 else sizemstr
    return sizemstr + sizeunit + ('B' if bsuffix and power else '')


def ParseBytes(bytesize, rounded=False, bsuffix=False):
    multends = next((
        i for i, c in enumerate(bytesize) if c not in digits + '.-'
    ), None)

    if multends is None:
        sizemstr, sizeunit = bytesize, ''
    else:
        if bsuffix and not bytesize.endswith('B'):
            raise Exception("incorrect size unit")
        else:
            bytesize = bytesize.rstrip('B')
        sizemstr, sizeunit = bytesize[:multends], bytesize[multends:]

    power = sizeunits.index(sizeunit)
    sizemult = Decimal(sizemstr)
    if rounded:
        sizemult = sizemult.quantize(Decimal('0.001'))
    bytesize = (sizemult * (1000 ** power)).quantize(1)
    return int(bytesize)


def format_indent(text, indent=4):
    indent = " " * indent
    return "\n".join(
        indent + line + indent for line in
        text.splitlines()
    )


def format_digest(text, length=48):
    return "\n".join(
        text[i:i+length] for i in
        xrange(0, len(text), length)
    ).upper()


def format_column(text, column):
    if len(text) > column:
        return text[:column-3] + "..."
    else:
        return text
