#!/usr/bin/python

from socket import inet_aton, inet_ntoa, error as socket_error

import ram.context


with ram.context(__name__):
    from wiz.utils import ValidateNonEmpty, ValidateIntRange


def ValidateHostname(value, length=None, allow_empty=False):
    if not value:
        return ValidateNonEmpty(value) if not allow_empty else ""
    value = value.decode('utf8').encode('idna')
    labels = value.split(".")
    if all(label.isdigit() for label in labels):
        raise ValueError("%s is assumed to be an IPv4 address" % value)
    isfqdn = not labels[-1]
    if isfqdn:
        labels = labels[:-1]
    length = length or (254 if isfqdn else 253)
    if len(value) > length:
        raise ValueError("value too long")
    for label in labels:
        if label.startswith("-") or label.endswith("-"):
            raise ValueError("label cannot start or end with hyphen")
        if not label.replace("-", "").isalnum():
            raise ValueError("only alphanumeric characters and hyphens allowed in labels")
    return value


def ValidatePort(value, allow_empty=False, allow_zeros=False, banned=None):
    if not value:
        return ValidateNonEmpty(value) if not allow_empty else ""
    try:
        rangemin, rangemax = 1, 0x10000 - 1
        return ValidateIntRange(value, rangemin=rangemin, rangemax=rangemax, banned=banned)
    except ValueError as err:
        raise ValueError("%s. Should be integer in range %s-%s" % (err, rangemin, rangemax))


def ValidatePortOrEmpty(value, allow_zeros=False, banned=None):
    return ValidatePort(value, allow_empty=True, allow_zeros=allow_zeros, banned=banned)


def ValidateIpV4(value, allow_empty=False, allow_zeros=False, allow_bcast=False):
    if not value:
        return ValidateNonEmpty(value) if not allow_empty else ""
    try:
        ipv4 = inet_aton(value)
        if not inet_ntoa(ipv4) == value:
            raise socket_error("is not in canonical form")
        if not allow_zeros and ipv4 == '\x00\x00\x00\x00':
            raise ValueError("0.0.0.0 address cannot be used")
        if not allow_bcast and ipv4 == '\xff\xff\xff\xff':
            raise ValueError("255.255.255.255 address cannot be used")
        return inet_ntoa(ipv4)
    except socket_error:
        raise ValueError("%s is not valid IPv4 address" % value)


def ValidateCIDR(value, allow_empty=False):
    if not value:
        return ValidateNonEmpty(value) if not allow_empty else ""
    ipaddr, _, prefix = value.partition("/")
    try:
        prefix = ValidateIntRange(prefix, rangemin=0, rangemax=32) if _ else prefix
    except ValueError as err:
        raise ValueError("prefix %s" % err)
    return ValidateIpV4(ipaddr, allow_zeros=True, allow_bcast=True) + (_ + prefix if _ else "")


def ValidateEmptyOrIpV4(value):
    return ValidateIpV4(value, allow_empty=True)


def ValidateEmptyOrHostname(value):
    return ValidateHostname(value, allow_empty=True)


def ValidateHostnameOrIpV4(value):
    try:
        return ValidateIpV4(value)
    except ValueError as err:
        return ValidateHostname(value)


def ValidateHostnameOrCIDR(value):
    try:
        return ValidateCIDR(value)
    except ValueError as err:
        return ValidateHostname(value)


def ValidateEndPoint(value):
    host, _, port = value.partition(":")
    if port:
        ValidatePort(port)
    ValidateHostnameOrIpV4(host)
    return value


def ValidateDomainList(value):
    errs = []
    for domain in value.split():
        try:
            ValidateHostname(domain, domain)
        except ValueError as err:
            errs += [err]
    if errs:
        raise ValueError(*errs)
    return value


from probe import GetHwIfacesList
from probe import GetHwIfaceIpAddress


def list_ip_addrs(include=None, exclude=None):
    include = set(include or [])
    exclude = set(exclude or [])

    ifaces = set(filter(GetHwIfaceIpAddress, GetHwIfacesList(skip_lo=True)))
    ifaces |= include
    ifaces -= exclude

    ip_addrs = map(GetHwIfaceIpAddress, ifaces)

    return dict(zip(ifaces, ip_addrs))


def format_ip_addrs(fmt, fmt_strs=None, include=None, exclude=None):
    ip_addrs = list_ip_addrs(include, exclude)

    def _fmt_with(addr):
        return fmt % (
            dict(fmt_strs, _=addr) if fmt_strs else
            addr
        )

    if not ip_addrs:
        return "No successfully configured interfaces found!"
    else:
        return "\n".join(map(_fmt_with, ip_addrs.values()))
