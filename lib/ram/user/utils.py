#!/usr/bin/python

import random
import string
import cracklib

cracklib.FascistCheck_ = cracklib.FascistCheck
cracklib.FascistCheck = lambda passwd, pwdict=None: (
    cracklib.FascistCheck_(passwd, pwdict) if pwdict is not None else
    None
)


import ram.context


with ram.context(__name__):
    from wiz.utils import ValidateNonEmpty


_first_chars = string.ascii_letters
_other_chars = string.ascii_letters + string.digits + '-'


def ValidateUsername(value, banned=None):
    if banned is not None and value in banned:
        raise ValueError("cannot be `%s`" % value)
    elif len(value) >= 31:
        raise ValueError("too long")
    elif not (((value[0] in _first_chars) if value else True) and all(c in _other_chars for c in value)):
        raise ValueError("contains symbols that aren't allowed")
    else:
        return ValidateNonEmpty(value)


def ValidatePassword(newpass, oldpass=None, pwdict=None):
    pwlen = len(newpass)
    # minimum of 8 characters, minimum of 3 character classes.
    # it's handled via character class credit variables.
    cracklib.MIN_LENGTH = max(8, pwlen) + 3 + int(pwlen < 8)
    # reduce similarity tolerance in case of short passwords.
    cracklib.DIFF_OK = min(5, pwlen / 2)

    return cracklib.VeryFascistCheck(newpass, oldpass, pwdict or None)


ValidatePasswordRequirements = (
    "The following requirements are in effect:\n"
    "  - it must be at least 8 characters long;\n"
    "  - it must contain at least 3 different\n"
    "    groups of symbols: latin lowercase, latin\n"
    "    uppercase, digits and special symbols;\n"
    "  - it can not be similar to username.\n"
)


def ValidateBasePassword(password, username, pwdict=None):
    try:
        return ValidatePassword(password, username, pwdict)
    except ValueError as eorig:
        try:
            ValidatePassword(password, None, pwdict).split('') # force valueerror
        except ValueError as epass:
            if str(eorig) != str(epass):
                raise ValueError("based on username")
            else:
                raise


def ValidateSamePassword(password, confirm, username, pwdict=None):
    if not password == confirm:
        raise ValueError("doesn't match")
    else:
        return (
            ValidateNonEmpty(password) and
            ValidateBasePassword(password, username, pwdict)
        )


def GenerateSalt(len=8):
    return "".join(random.choice(string.ascii_letters + string.digits + "./") for n in range(len))


def HiddenText(s):
    return "".join("*" for c in s)
