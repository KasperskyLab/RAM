from collections import OrderedDict
from ram.osutils import TrySubmit

__ETC_HOSTS = '/etc/hosts'


def __list_aliases():
    ret = OrderedDict()
    lines = open(__ETC_HOSTS).readlines()
    for i, line in enumerate(lines[:]):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        ip, hosts = line.split(None, 1)
        hosts = hosts.split()
        if ip in ret:
            ret[ip].extend(hosts)
        else:
            ret[ip] = hosts
    return ret


def __get_ips_for(hostname, data=None):
    if not hostname:
        raise ValueError()

    if not data:
        data = __list_aliases()
    return (k for k, v in data.items() if hostname in v)


def __write_aliases(aliases):
    lines = ['%s\t%s\n' % (ip, ' '.join(hosts)) for ip, hosts in aliases.items()]
    if not TrySubmit(__ETC_HOSTS, lines):
        raise IOError('Failed to update %s' % __ETC_HOSTS)


def get_ip_for(hostname):
    return next(__get_ips_for(hostname), None)


def create_alias(ip, hostname):
    data = __list_aliases()
    for ip_alias in __get_ips_for(hostname, data):
        data[ip_alias].remove(hostname)
        if not data[ip_alias]:
            del data[ip_alias]

    if ip and hostname:
        if ip not in data:
            data[ip] = []
        data[ip].append(hostname)

    __write_aliases(data)


def update_localhost_alias(hostname):
    def not_local(alias):
        return alias.partition(".")[0] not in ("localhost", "localhost4", "localhost6", "centralnode")

    localhost_ips = list(__get_ips_for('localhost'))
    data = __list_aliases()
    for ip, aliases in data.items():
        if ip not in localhost_ips:
            continue
        map(data[ip].remove, filter(not_local, aliases))
        if hostname not in data[ip]:
            data[ip].append(hostname)

    __write_aliases(data)
