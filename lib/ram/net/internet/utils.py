#!/usr/bin/python

from urllib import splittype, splithost, splitnport, splituser, splitpasswd

import ram.context


with ram.context(__name__):
    from net.utils import ValidateEndPoint


def ParseUrl(value):
    type = ""
    host = ""
    port = ""
    path = ""
    username = ""
    password = ""

    type, value = splittype(value or "")
    value, path = splithost(value or "")
    usps, value = splituser(value or "")
    if usps:
        username, password = splitpasswd(usps)
    host, port = splitnport(value or "", None)

    return type or "", host or "", str(port) if port else "", path or "", username or "", password or ""


def ValidateUrl(value, proto=None, allow_path=True):
    type, host, port, path, username, password = ParseUrl(value)
    if proto and not type in proto:
        raise ValueError("unsupported protocol type")
    if path and path != '/' and not allow_path:
        raise ValueError("path component of url is not allowed")
    ValidateEndPoint("%s:%s" % (host, port))
    return value


def BuildUrl(type, host, port=0, path="", username="", password=""):
    if password:
        password = ":" + password
    if username:
        username = username + password + "@"
    if port:
        host = host + ":" + str(port)
    if type:
        type = type + "://"
    else:
        type = ""
    return type + username + host + path
