#!/usr/bin/python

import struct

from fcntl import ioctl
from socket import socket, AF_INET, SOCK_DGRAM
from socket import inet_aton, inet_ntoa, gethostbyname, gaierror

SIOCGIFFLAGS = 0x8913
SIOCGIFADDR = 0x8915
SIOCGIFNETMASK = 0x891b
SIOCGIFHWADDR = 0x8927

ARPHRD_LOOPBACK = 772

_NETDEV_FILENAME = '/proc/net/dev'
_NETTCP_FILENAME = '/proc/net/tcp'
_ROUTES_FILENAME = '/proc/net/route'
_RESOLV_FILENAME = '/etc/resolv.conf'


def _listNetworkInterfaces():
    lines = open(_NETDEV_FILENAME).readlines()[2:]
    return [line.partition(":")[0].strip() for line in lines]


def _doNetdeviceIoctl(ifname, request, format):
    sock = socket(AF_INET, SOCK_DGRAM)
    data = struct.pack('16s16x', ifname[:16])
    data = ioctl(sock.fileno(), request, data)
    return struct.unpack(format, data[16:])


def GetHwIfaceType(ifname):
    try:
        return _doNetdeviceIoctl(ifname, SIOCGIFHWADDR, 'H14s')[0]
    except IOError:
        return None


def GetHwIfaceAddr(ifname):
    try:
        hwtype, hwaddr = _doNetdeviceIoctl(ifname, SIOCGIFHWADDR, 'H14s')
        if hwtype == 1:
            return ":".join(["%02X" % ord(c) for c in hwaddr[:6]])
        else:
            return ""
    except IOError:
        return ""


def GetHwIfacesByType(type):
    ifaces = _listNetworkInterfaces()
    return [ifname for ifname in ifaces if (GetHwIfaceType(ifname) == type)]


def IsLoopbackIface(ifname):
    return ifname in GetHwIfacesByType(ARPHRD_LOOPBACK)


def GetLoopbackIface():
    return GetHwIfacesByType(ARPHRD_LOOPBACK)[0]


def GetHwIfaceFlags(ifname):
    try:
        return _doNetdeviceIoctl(ifname, SIOCGIFFLAGS, 'H14x')[0]
    except IOError:
        return 0


def GetHwIfacesByFlag(flag):
    ifaces = _listNetworkInterfaces()
    return [ifname for ifname in ifaces if (GetHwIfaceFlags(ifname) & flag)]


def GetHwIfacesByAddr(addr):
    if not addr:
        return []
    ifaces = _listNetworkInterfaces()
    return [ifname for ifname in ifaces if (GetHwIfaceAddr(ifname) == addr)]


def GetHwIfacesList(skip_lo=False):
    ifaces = _listNetworkInterfaces()
    if skip_lo:
        ifaces.remove(GetLoopbackIface())
    return ifaces


def GetHwIfaceIpAddress(ifname):
    try:
        iptype, ipaddr = _doNetdeviceIoctl(ifname, SIOCGIFADDR, 'H2x4s8x')
        if iptype == 2:
            return ".".join(["%u" % ord(c) for c in ipaddr])
    except:
        pass
    return ''


def GetHwIfaceIpNetmask(ifname):
    try:
        iptype, ipmask = _doNetdeviceIoctl(ifname, SIOCGIFNETMASK, 'H2x4s8x')
        if iptype == 2:
            return ".".join(["%u" % ord(c) for c in ipmask])
    except:
        pass
    return ''


def _inet_atoi(address):
    return struct.unpack('!I', inet_aton(gethostbyname(address)))[0]


def _inet_itoa(address):
    return inet_ntoa(struct.pack('!I', address))


def IsLoopbackAddress(address):

    try:
        netaddr = GetHwIfaceIpAddress(GetLoopbackIface())
        netmask = GetHwIfaceIpNetmask(GetLoopbackIface())
        return bool(_inet_atoi(address) & _inet_atoi(netmask) == _inet_atoi(netaddr) & _inet_atoi(netmask))
    except gaierror:
        return False


def CanonicalizeAddr(address):
    try:
        return _inet_itoa(_inet_atoi(address))
    except gaierror:
        return ""


def GetHwIfaceByAddr(address):
    try:
        _address = _inet_atoi(address)
        if not _address:
            raise gaierror

        if IsLoopbackAddress(address):
            return GetLoopbackIface()

        for ifname in GetHwIfacesList(skip_lo=True):
            if _address == _inet_atoi(GetHwIfaceIpAddress(ifname)):
                return ifname
    except gaierror:
        pass

    return ""


def _listNetworkRoutes():
    lines = open(_ROUTES_FILENAME).readlines()
    title = lines.pop(0)
    return title.split(), [line.split() for line in lines]


def GetRoutes(*args, **kwargs):
    title, routes = _listNetworkRoutes()
    for k in kwargs:
        try:
            index = title.index(k)
            routes = [route for route in routes if route[index] == kwargs[k]]
        except ValueError:
            return []
    try:
        inlist = [title.index(v) for v in args]
        return [[route[i] for i in inlist] for route in routes]
    except ValueError:
        return []


def GetIpDefaultGateway():
    try:
        routes = GetRoutes('Gateway', Destination='00000000')
        gwaddr = int(routes[0][0], base=0x10) if routes and routes[0] else 0
        ipgate = struct.unpack('4s', struct.pack('I', gwaddr))[0] if gwaddr else ''
        return ".".join(["%u" % ord(c) for c in ipgate])
    except:
        return ""


def GetResolvNameservers():
    try:
        lines = open(_RESOLV_FILENAME).readlines()
        return [line.partition(" ")[2].strip() for line in lines if line.startswith('nameserver')]
    except:
        return []


def GetTcpPortsInUse():
    lines = open(_NETTCP_FILENAME).readlines()[1:]
    for line in lines:
        toks = line.split()
        if int(toks[3], 0x10) == 0x0A:
            addr, _, port = toks[1].partition(':')
            yield int(port, 0x10)


def GetTcpPortsInUseBy(pname):
    from ram import process

    lines = process.output('netstat -lntp').splitlines()[2:]
    for line in lines:
        proto, rq, sq, local, remote, state, owner = line.split(None, 6)
        owner = owner.strip()
        if owner == '-':
            continue
        _pid, _, _cmd = owner.partition('/')
        _pname = _cmd.split().pop(0)
        if _pname == pname[:len(_pname)]:
            addr, _, port = local.rpartition(':')
            yield int(port)


if __name__ == '__main__':
    # find ethernet devices
    print "ethernet devices:\t%s" % GetHwIfacesByType(1)
    # find up devices
    print "available devices:\t%s" % GetHwIfacesByFlag(1)
    # find running devices
    print "running devices:\t%s" % GetHwIfacesByFlag(0x40)

    print "interfaces list:\t%s" % GetHwIfacesList()
