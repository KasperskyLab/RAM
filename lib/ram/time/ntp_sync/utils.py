import os
import ram.process


def is_ntpd_enabled():
    return ram.process.launch('chkconfig ntpd &>/dev/null') == 0


def query_ntp_servers():
    servers = []
    status, output, errors = ram.process.run('cat /etc/ntp.conf | grep "^server\s"')
    if status != 0:
        return servers

    for item in (l.rstrip().split() for l in output.rstrip(os.linesep).split(os.linesep)):
        if len(item) > 1 and item[1].rstrip():
            servers.append(item[1].rstrip())
    return servers


def store_ntp_servers(servers):
    status, output, errors = ram.process.run('cat /etc/ntp.conf | grep -v "^servers\?\s"')
    ntp_cfg = output if status == 0 else ''

    if ntp_cfg[-1:] != os.linesep:
        ntp_cfg += os.linesep

    for server in servers:
        if server:
            ntp_cfg += 'server %s%s' % (server, os.linesep)

    with open('/etc/ntp.conf', 'w') as f:
        f.write(ntp_cfg)


def store_ntpd_enabled(enabled):
    ram.process.launch('chkconfig ntpd %s' % ('on' if enabled else 'off'))
