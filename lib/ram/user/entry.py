#!/usr/bin/python

import crypt

import ram.widgets

from utils import ValidateUsername, ValidateSamePassword
from utils import ValidatePasswordRequirements, GenerateSalt


SLT = None
MD5 = 1
SHA256 = 5
SHA512 = 6


def RunUsernamePasswordInput(header, text, username="", password="", editable=True, hashes=None, banned=None, forced=False, pwdict=None):
    if (username and not editable) or banned is None:
        banned = []

    try:
        username = ValidateUsername(username) if username else ""
    except ValueError as err:
        raise RuntimeError("username: " + str(err))

    if not hashes:
        raise RuntimeError("At least one hash algorithm should be specified.")

    if password and not password.startswith("$"):
        raise RuntimeError("Old password is not encrypted with the given hash.")

    class AccountValidate(object):
        def __init__(self, *args):
            if len(args) != 4:
                args = args[:1] + ("",) + args[1:]
            self.username, self.oldpass, self.newpass, self.confirm = args

        def username_check(self, value):
            return ValidateUsername(value, banned=banned)

        def newpass_check(self, value):
            return ValidateSamePassword(self.newpass, self.confirm, self.username, pwdict=pwdict)

        def oldpass_check(self, value, password=password):
            prefix, sep, hashed = password.rpartition("$")
            if crypt.crypt(value, prefix + sep) == password:
                return value
            else:
                raise ValueError("incorrect password entered")

    username_fixed = "" if not username or editable else "="
    if not password:
        username, password, _ = ram.widgets.RunEntry(
            header, text + ValidatePasswordRequirements,
            [
                (username_fixed + "Username", username, AccountValidate.username_check),
                ("_Password", "", AccountValidate.newpass_check),
                ("_Confirm password", "", None),
            ],
            initContext=AccountValidate,
            allowCancel=not forced,
            waitCorrect=forced
        )
    else:
        username, _, password, _ = ram.widgets.RunEntry(
            header, text + ValidatePasswordRequirements,
            [
                (username_fixed + "Username", username, AccountValidate.username_check),
                ("_Old Password", "", AccountValidate.oldpass_check),
                ("_New Password", "", AccountValidate.newpass_check),
                ("_Confirm password", "", None),
            ],
            initContext=AccountValidate,
            allowCancel=not forced,
            waitCorrect=forced
        )

    def password_crypt(password, hashid):
        salt = ("$%s$%s$" % (hashid, GenerateSalt(8))) if hashid else (GenerateSalt(2))
        return crypt.crypt(password, salt) if password else ""

    return [username] + [password_crypt(password, hashid) for hashid in hashes]
