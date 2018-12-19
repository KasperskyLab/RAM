``print`` service
=================

The ``print`` command introduced in the previous releases allows printing unit configuration
storage as key-value pairs. Output of this command is human-readable and suitable for machine parsing.
To make sure that the command output is up to date, run the ``query`` command first:

.. sourcecode:: console

    # ram query ifconfig
    $ ram print ifconfig
    eth0.devname=eth0
    eth0.enabled=eth0
    eth0.hw_addr=08:00:27:CA:EF:21
    eth0.ip_used=10.16.106.57
    eth0.usedhcp=dhcp
    eth2.devname=eth2
    eth2.hw_addr=08:00:27:E6:C1:3B
    eth2.usedhcp=dhcp
    ifaces=eth0 eth2
    lo.devname=lo
    lo.enabled=lo

Since the release 0.2.0 of ram framework, it is possible to specify a key name as a ``print`` command argument
to print only its value. The key name will not be included in the output. This feature is intended for shell scripts
and designed to be shell-friendly. For example, lists are displayed as space separated strings which are
suitable for using with the ``for`` shell construct. For boolean values, a missing key-value pair or an empty value
indicate ``false`` and a non-empty value indicates ``true``:

.. sourcecode:: console

    $ ram print ifconfig ifaces
    eth0 eth2
    $ ifaces=`ram print ifconfig ifaces`
    $ for ifname in $ifaces do ram print ifconfig ${ifname}.hw_addr; done
    08:00:27:CA:EF:21
    08:00:27:E6:C1:3B
    $ eth0=`ram print ifconfig eth0.enabled`
    $ [ -n "$eth0" ] && echo "enabled" || echo "disabled"
    enabled
    $ eth1=`ram print ifconfig eth1.enabled`
    $ [ -n "$eth1" ] && echo "enabled" || echo "disabled"
    disabled
    $ eth2=`ram print ifconfig eth2.enabled`
    $ [ -n "$eth2" ] && echo "enabled" || echo "disabled"
    disabled
