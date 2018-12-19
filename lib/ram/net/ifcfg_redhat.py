#!/usr/bin/python

from glob import iglob
from collections import OrderedDict
from itertools import count as itercount

import ram.process

from ram.osutils import FileStamp
from ram.formats import env


_NETWORKCFG = '/etc/sysconfig/network'
_NETWORKSRV = '/etc/init.d/network'
_NETWORKRUN = '/var/lock/subsys/network'
_IFCFG_ROOT = '/etc/sysconfig/network-scripts/'
_IFCFG_PATH = _IFCFG_ROOT + 'ifcfg-'
_ROUTE_PATH = _IFCFG_ROOT + 'route-'
_IFCFG_GLOB = _IFCFG_PATH + '*'


class NetworkConfiguration(object):
    DEFAULT_NETCONF = {
        'ONBOOT': 'yes',
        'BOOTPROTO': 'dhcp',
        'PERSISTENT_DHCLIENT': 'yes',
        'DEFROUTE': 'no',
        'PEERDNS': 'no',
    }
    DEFLOOP_NETCONF = {
        'ONBOOT': 'yes',
        'IPADDR': '127.0.0.1',
        'NETMASK': '255.0.0.0',
        'NETWORK': '127.0.0.0',
        'BROADCAST': '127.255.255.255',
    }

    def __init__(self, config, ifcfgs, routes):
        self.config = config
        self.ifcfgs = ifcfgs
        self.routes = routes

    def __iter__(self):
        for ifname in self.ifcfgs:
            if self.ifcfgs[ifname]:
                yield ifname

    def _modify_settings(net_config_method):
        def _modify_settings_wrapper(self, ifname, *args, **kwargs):
            if not ifname:
                ifname = 'lo'
            net_config_method(self, ifname, *args, **kwargs)
        return _modify_settings_wrapper

    def IsModified(self):
        return any([md.IsModified() for md in [self.config] + self.ifcfgs.values() + self.routes.values()])

    def IsLoopback(self, ifname):
        return ifname == 'lo'

    @_modify_settings
    def DelIface(self, ifname):
        if self.IsLoopback(ifname):
            return
        if ifname == self.config['GATEWAYDEV']:
            del self.config['GATEWAYDEV']
        self.ifcfgs[ifname].clear()
        self.routes[ifname].clear()

    @_modify_settings
    def AddIface(self, ifname, defconf=False):
        self.ifcfgs[ifname] = env.cfgopen(_IFCFG_PATH + ifname, readonly=False, delempty=True)
        self.ifcfgs[ifname].update(self.DEFLOOP_NETCONF if self.IsLoopback(ifname) else self.DEFAULT_NETCONF)
        self.ifcfgs[ifname]['DEVICE'] = ifname
        self.ifcfgs[ifname]['DEFCONF'] = 'yes' if defconf else 'no'
        self.routes[ifname] = env.cfgopen(_ROUTE_PATH + ifname, readonly=False, delempty=True)

    def GetIfaceDefConf(self, ifname):
        if self.IsLoopback(ifname):
            return False
        defconf = self.ifcfgs[ifname]['DEFCONF'] or 'no'
        return defconf.lower() == 'yes'

    def GetIfaceDevName(self, ifname):
        return self.ifcfgs[ifname]['DEVICE'] or ifname

    @_modify_settings
    def SetIfaceDevName(self, ifname, devname):
        if self.IsLoopback(ifname):
            return
        self.ifcfgs[ifname]['DEVICE'] = devname

    def GetIfaceBootProto(self, ifname):
        bootproto = self.ifcfgs[ifname]['BOOTPROTO']
        if bootproto in ['dhcp', 'bootp']:
            return bootproto

        return ''

    @_modify_settings
    def SetIfaceBootProto(self, ifname, bootproto):
        if self.IsLoopback(ifname) or (bootproto not in ['dhcp', 'bootp']):
            bootproto = 'none'
        else:
            self.ifcfgs[ifname]['PERSISTENT_DHCLIENT'] = 'yes'
        self.ifcfgs[ifname]['BOOTPROTO'] = bootproto

    def GetIfaceEnabled(self, ifname):
        if self.IsLoopback(ifname):
            return True
        enabled = self.ifcfgs[ifname]['ONBOOT'] or 'yes'
        return not (enabled.lower() == 'no')

    @_modify_settings
    def SetIfaceEnabled(self, ifname, enabled):
        if self.IsLoopback(ifname):
            return
        self.ifcfgs[ifname]['ONBOOT'] = 'yes' if enabled else 'no'

    def GetIfaceIpAddress(self, ifname):
        for suffix in ['', '0']:
            if 'IPADDR' + suffix in self.ifcfgs[ifname]:
                return self.ifcfgs[ifname]['IPADDR' + suffix]
        return ''

    @_modify_settings
    def SetIfaceIpAddress(self, ifname, ip_addr):
        self.ifcfgs[ifname]['IPADDR'] = ip_addr
        if 'IPADDR0' in self.ifcfgs[ifname]:
            del self.ifcfgs[ifname]['IPADDR0']

    def GetIfaceIpNetmask(self, ifname):
        for suffix in ['', '0']:
            if 'NETMASK' + suffix in self.ifcfgs[ifname]:
                return self.ifcfgs[ifname]['NETMASK' + suffix]
        return ''

    @_modify_settings
    def SetIfaceIpNetmask(self, ifname, netmask):
        self.ifcfgs[ifname]['NETMASK'] = netmask
        if 'NETMASK0' in self.ifcfgs[ifname]:
            del self.ifcfgs[ifname]['NETMASK0']

    def GetPeerDnsDevice(self):
        for ifname in reversed(list(self)):
            if self.IsLoopback(ifname):
                continue
            if not (self.ifcfgs[ifname]['PEERDNS'] or 'no') == 'no':
                return ifname
        return ''

    @_modify_settings
    def SetPeerDnsDevice(self, ifname):
        for ifover in reversed(list(self)):
            if ifover != ifname:
                self.ifcfgs[ifover]['PEERDNS'] = 'no'
            else:
                self.ifcfgs[ifover]['PEERDNS'] = 'yes'

    def GetIfacePrimaryDns(self, ifname):
        return self.ifcfgs[ifname or "lo"]['DNS1']

    def GetIfaceSecondaryDns(self, ifname):
        return self.ifcfgs[ifname or "lo"]['DNS2']

    @_modify_settings
    def SetIfacePrimaryDns(self, ifname, srvaddr):
        self.ifcfgs[ifname]['DNS1'] = srvaddr

    @_modify_settings
    def SetIfaceSecondaryDns(self, ifname, srvaddr):
        self.ifcfgs[ifname]['DNS2'] = srvaddr

    def GetIfaceSearchList(self, ifname):
        return self.ifcfgs[ifname or "lo"]['DOMAIN']

    @_modify_settings
    def SetIfaceSearchList(self, ifname, domlist):
        self.ifcfgs[ifname]['DOMAIN'] = domlist

    def GetGatewayDevice(self):
        device = self.config['GATEWAYDEV']
        for ifname in [device] if device in self.ifcfgs else reversed(list(self)):
            if self.IsLoopback(ifname):
                continue
            if not (self.ifcfgs[ifname]['DEFROUTE'] or 'yes') == 'no':
                return ifname
        return ''

    @_modify_settings
    def SetGatewayDevice(self, ifname):
        if self.IsLoopback(ifname):
            ifname = ''
        for ifover in reversed(list(self)):
            if ifover != ifname:
                self.ifcfgs[ifover]['DEFROUTE'] = 'no'
            else:
                self.ifcfgs[ifover]['DEFROUTE'] = 'yes'
        self.config['GATEWAYDEV'] = ifname

    def GetIfaceIpGateway(self, ifname):
        return self.ifcfgs[ifname]['GATEWAY'] or self.config['GATEWAY']

    @_modify_settings
    def SetIfaceIpGateway(self, ifname, gateway):
        self.config['GATEWAY'] = ''
        self.ifcfgs[ifname]['GATEWAY'] = gateway

    def GetIfaceGwIgnored(self, ifname):
        return (self.ifcfgs[ifname]['DHCLIENT_IGNORE_GATEWAY'] or 'no') == 'yes'

    @_modify_settings
    def SetIfaceGwIgnored(self, ifname, ignored):
        self.ifcfgs[ifname]['DHCLIENT_IGNORE_GATEWAY'] = 'yes' if ignored else 'no'

    def GetIfaceStaticRoutes(self, ifname):
        rtlist = []
        for i in itercount():
            address = self.routes[ifname]['ADDRESS%u' % i]
            if not address:
                break
            netmask = self.routes[ifname]['NETMASK%u' % i]
            if not netmask:
                continue
            gateway = self.routes[ifname]['GATEWAY%u' % i]
            rtlist += [(address, netmask, gateway)]
        return rtlist

    @_modify_settings
    def SetIfaceStaticRoutes(self, ifname, rtlist):
        self.routes[ifname].clear()
        for i, (address, netmask, gateway) in enumerate(rtlist):
            self.routes[ifname]['ADDRESS%u' % i] = address
            self.routes[ifname]['NETMASK%u' % i] = netmask
            self.routes[ifname]['GATEWAY%u' % i] = gateway

    def GetHostname(self):
        return self.config['HOSTNAME'] or self.config['DHCP_HOSTNAME']

    def SetHostname(self, hostname):
        self.config['HOSTNAME'] = hostname
        self.config['DHCP_HOSTNAME'] = hostname

    def GetIfaceProperty(self, ifname, prop):
        return self.ifcfgs[ifname][prop]

    @_modify_settings
    def SetIfaceProperty(self, ifname, prop, value):
        self.ifcfgs[ifname][prop] = value


def _isValidConfigurationFilename(filename):
    return not filename.endswith(('.rpmsave', '.rpmnew', '-range', '~'))


# network service walk through interfaces list in special
# order given by sed+sort shell expression which is hard
# to emulate using python. Therefore to keep interface order
# in sync with network service this function just parses
# output of service command. Some kind of fallback should
# be used in case of errors.

def _getServiceIfConfigIter():
    try:
        output = ram.process.output([_NETWORKSRV, 'status'])
        _lines = output.splitlines()
        if _lines[0] == 'Configured devices:':
            return (_IFCFG_PATH + ifname for ifname in _lines[1].split())
    except Exception:
        pass
    return None


def _getDefaultIfConfigIter():
    return (ifconf for ifconf in iglob(_IFCFG_GLOB) if _isValidConfigurationFilename(ifconf))


def QueryNetworkConfiguration(error_cb=None):
    config = env.cfgopen(_NETWORKCFG, readonly=False, error_cb=error_cb)

    ifiter = _getServiceIfConfigIter() or _getDefaultIfConfigIter()

    ifcfgs = OrderedDict()
    routes = OrderedDict()
    for fname in ifiter:
        short = fname[len(_IFCFG_PATH):]
        route = _ROUTE_PATH + short
        ifcfgs[short] = env.cfgopen(fname, readonly=False, delempty=True, error_cb=error_cb)
        routes[short] = env.cfgopen(route, readonly=False, delempty=True, error_cb=error_cb)

    return NetworkConfiguration(config, ifcfgs, routes)


def NetworkConfigurationStamp():
    tstamp = max([FileStamp(_NETWORKCFG), FileStamp(_IFCFG_ROOT)])

    ifiter = _getServiceIfConfigIter() or _getDefaultIfConfigIter()

    for fname in ifiter:
        short = fname[len(_IFCFG_PATH):]
        route = _ROUTE_PATH + short
        tstamp = max([tstamp, FileStamp(fname), FileStamp(route)])

    return tstamp


def NetworkServiceRunInEffect():
    return FileStamp(_NETWORKRUN)


def StoreNetworkConfiguration(netconf):
    if not netconf.config or not netconf.ifcfgs:
        raise RuntimeError('Attempting to store empty configuration')

    netconf.config.sync()

    ifiter = _getServiceIfConfigIter() or _getDefaultIfConfigIter()

    for fname in ifiter:
        short = fname[len(_IFCFG_PATH):]
        route = _ROUTE_PATH + short
        if short not in netconf.ifcfgs:
            env.cfgopen(fname, readonly=False, delempty=True).sync()
            env.cfgopen(route, readonly=False, delempty=True).sync()

    for short in netconf.ifcfgs:
        netconf.ifcfgs[short].sync()
        netconf.routes[short].sync()


if __name__ == '__main__':
    from sys import stderr, argv

    def dump_to_stderr(file, lnum, emsg):
        print >> stderr, "File %s: Line %s: %s" % (file, lnum, emsg)

    if argv[1:]:
        for filename in argv[1:]:
            result = env.cfgopen(filename, error_cb=dump_to_stderr)
            print "%s: %s" % (filename, result)
    else:
        netconf = QueryNetworkConfiguration(error_cb=dump_to_stderr)
        print netconf.config
        print netconf.ifcfgs
        print netconf.routes
