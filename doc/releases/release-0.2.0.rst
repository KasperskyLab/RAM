Release 0.2.0 (2016-06-06)
==========================


End User Changes
----------------


The ``tweak`` command
~~~~~~~~~~~~~~~~~~~~~

The ``tweak`` command allows managing internal ram options that affect framework behavior.
The options are system-wide and their values are persistent. In general usage of options is
intended for development and debugging purposes. Without arguments, the ``tweak`` command prints
all available options and their values:

.. sourcecode:: console

    $ ram tweak
    debug=off
    apply=off
    shell=off
    local=off

To get value of the option, pass it's name to the ``tweak`` command as an argument:

.. sourcecode:: console

    $ ram tweak debug
    debug=off

To set value of the option, pass it's name and value to the ``tweak`` command as arguments. For boolean options 
following values will be accepted: ``on``/``off``, ``yes``/``no``, ``true``/``false`` and ``1``/``0``:

.. sourcecode:: console

    # ram tweak debug on
    # ram tweak debug 1

The following options are available in the release 0.2.0:

``debug``
    Enables debug output.

``apply``
    Forces ram to automatically run the ``apply`` action
    for a unit after its ``setup`` action has completed.

``shell``
    Switches to the usage of ``os.system`` instead of ``subprocess`` if possible.

``local``
    Allows lookup and execution of ram units from local paths.


The ``print`` command
~~~~~~~~~~~~~~~~~~~~~

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


The ``apply`` command
~~~~~~~~~~~~~~~~~~~~~

The earlier versions of ram framework (prior to release 0.2.0) only allow querying, modifying and storing
configurations to the corresponding configuration files. However, it is usually required to restart
the corresponding services to apply changes, so a user has to remember what services to restart or what commands
to run.

The 0.2.0 version of ram framework allows unit developers to create ``apply`` actions for their units.
The ``apply`` action is a regular shell script that takes care of services related to settings managed by unit.
To avoid excessive service restarts, unit developer has to add checks if settings in effect are the same
as settings in configuration files.

In the earlier version of ram framework (prior to release 0.2.0) the ``apply`` action is used to copy configuration
from unit storage to the actual system configs. In the current version, role of the ``apply`` action is redefined
for applying changes to a running system and the ``store`` action is used for updating system configs.
As a result, a typical ram unit session looks as follows:

.. sourcecode:: console

    # # query from system configs and put values to unit's storage
    # ram query ifconfig

    # # run actual end user interaction using front end
    # ram input ifconfig

    # # get values from unit's storage and store to system configs
    # ram store ifconfig

    # # meta-action setup could be used to run query/input/store in sequence
    # ram setup ifconfig

    # # apply system configs in effect
    # ram apply ifconfig


It is not always required to apply settings right after they have been edited. By default, The ``apply`` action
has to be invoked separately and not run by the ``setup`` meta-action. It is possible to change this behavior using
the ``apply`` option managed by the``tweak`` command. If this option is set, the ``apply`` action is invoked after
each successful ``setup`` action:

.. sourcecode:: console

    # ram tweak apply on

    # # no need for separate apply invocation now
    # ram setup ifconfig

The option is persistent and system-wide. Once set, it applies to every invocation of the ``setup`` action on the machine.


Developer Changes
-----------------


Unit cache and local units
~~~~~~~~~~~~~~~~~~~~~~~~~~

The earlier versions of ram framework perform lookup outside of standard unit library in a current directory
and in the list of directories specified by ``RAMPATH`` environment variable. Due to inconvenience of managing
``RAMPATH`` for different users and different ram unit distributions this mechanism is now substituted with global
unit cache and local unit mechanisms.

By default, the current version of ram framework looks up for units only in its cache directory. To add
any redistributable units to cache, copy the top-level unit directory path into a file, place it in ``/etc/ram/``,
then run ``ram cache`` to update cache. To delete redistributable units from cache, remove the corresponding file
from ``/etc/ram/`` and run the ``ram cache`` command again, for example:

.. sourcecode:: console

    $ ram index
    stdunit1
    stdunit2
    $ ls .
    myunit1/ myunit2/
    # pwd >/etc/ram/myunits
    # ram cache
    $ ram index
    myunit1
    myunit2
    stdunit1
    stdunit2
    # rm -f /etc/ram/myunits
    # ram cache
    $ ram index
    stdunit1
    stdunit2

Thus, install/uninstall scripts or package hooks of redistributed ram units should manage the ``/etc/ram`` files
and invoke the ``ram cache`` command. To update cache for one specific unit only, add the unit name to the ``ram cache``
command as a argument:


.. sourcecode:: console

    # ram cache myunit


Local units are introduced to avoid running ``ram cache`` every time changes are committed to unit. To enable support
of local units, the ``local`` option should be set:

.. sourcecode:: console

    # ram tweak local on

Once local units are enabled, it is possible to use a regular directory path as a unit name, provided that the directory
includes ram unit files. If a directory and a unit in cache share the same name, local directory unit is preferred:

.. sourcecode:: console

    # ram setup /path/to/myunit
    # cd /path/to
    # ram setup ./myunit
    # ram setup myunit
    # cd ./myunit
    # ram setup .


Framework stores all runtime files (such as storage db and lock files) in local unit directory
instead of dedicated directories in /var hierarchy.

Bash completion distributed with ram framework recognizes the ``local`` option and provides regular
directories as completion options if this ram option is set.

It is recommended to avoid using local units on end user configurations.


Tagged action scripts
~~~~~~~~~~~~~~~~~~~~~

The earlier versions of ram framework use strict filenames for unit action scripts. Name of the script
should match the name of the related action name without extension. So, the ``query`` script is used to handle the
``query`` unit action, the ``store`` script is used to handle the ``store`` action, etc.

The current version of ram framework recognizes scripts with the action name followed by ``.`` and a custom
specifier string as secondary tagged action scripts. The primary origin action script (without specfier) is always
executed first; the secondary action scripts are executed afterwards with no strictly defined execution sequence.
As a result, none of these scripts related to the same action should depend on each other. Tagged scripts are
introduced to allow splitting code that handles different services with the same configuration domain.
The tagged script feature also allows implementing scripts in different languages (i.e. python and shell).

Example:

.. sourcecode:: console

    # ls proxywiz
    about
    query
    input
    store.yum
    store.env

The ``proxywiz`` unit provides two tagged ``store`` scripts. One of these scripts saves proxy configuration to yum config
file and the other one saves proxy configuration in user environment profiles. Be careful when running ``query`` scripts,
because they are executed in sequence and the latter scripts can override configuration queried by the previous ones.
In the example above, only one original ``query`` script is provided.

Cross-unit python imports
~~~~~~~~~~~~~~~~~~~~~~~~~

The previous versions of ram framework allowed importing py-modules provided by units using the following code:

.. sourcecode:: pycon

    >>> # old way
    >>> import ram.unitlib
    >>> import network.probe

Once ``ram.unitlib`` is imported, py-modules provided by units can be imported using unit name as top-level package.
This code imports ``probe.py`` from the ``network`` unit directory. Due to confusing stateful behaviour and risk of
name resolution conflicts with packages from python search path, this semantics has been improved to make it straight-forward:

.. sourcecode:: pycon

    >>> # new way
    >>> import ram.unitlib.network.probe

As a result, all found units are available as subpackages of ``ram.unitlib``. The standard library contains units that
provide only imports with no defined ram entry points (actions). These units are marked with the ``!`` symbol in the
output of the ``ram index`` command:

.. sourcecode:: console

    $ ram index
    account          !   Account configuration-related functions.
    adminwiz             Create new system user and set password.
    datetime             Configure system clock.
    diskwiz              Disk partitioning.
    eulawiz              Find suitable EULA files and ask user to agree on terms.
    generic          !   Generic functions for units.
    hostname             Configure hostname.
    ifconfig             Network interface configuration.
    internet         !   Internet URL manipulation functions for units.
    logview              View system logs using less.
    network          !   Network configuration-related functions for units.
    pipecat              Generic unit to display pipe data transfer progress.
    resolver             Configure DNS resolver.
    routing              Configure gateway and routes.
    timewiz              Generic time configuration.
    timezone             Configure timezone for the machine.

It is possible to apply the described import semantics not only in ram unit scripts but also in arbitrary python scripts
or even at python interactive interpreter.


Cross-unit storage access
~~~~~~~~~~~~~~~~~~~~~~~~~

Import mechanics described in the previous section also serves for cross-unit storage access. To retrieve
values from a storage db of another unit, top-level package referencing this unit should be imported. For example,
to access values from the ``ifconfig`` storage it is required to import ``ram.unitlib.ifconfig``. Once imported,
the module object acts as a dictionary with the same semantics as config dictionary for the running unit:

.. sourcecode:: pycon

    >>> from ram.unitlib import ifconfig
    >>> print ifconfig['ifaces']
    eth0 eth2

Before giving access to the storage db of the imported unit, ram framework attempts to run the ``query`` action for this
unit, but it may fail (with traceback printed in the console) if the caller has insufficient permissions to perform this
action. In this case the caller script execution is continued but the outdated information is provided.

The imported unit provides all its configuration values from the storage db in read-only mode. Framework does not prohibit
actual update of imported unit dictionary but values are not actually modified in the storage db.

Non-python scripts can also access values from other ram units using the ``ram print`` command:

.. sourcecode:: console

    # ram print ifconfig ifaces
    eth0 eth2

Python imports and the ``ram print`` command can be used not only in ram unit scripts but also in any arbitrary scripts.


``ConfigOpener`` objects
~~~~~~~~~~~~~~~~~~~~~~~~

Release 0.2.0 of ram framework introduces new entities to reduce boilerplate code writing in ``query`` and
``store`` scripts for ram units. In previous versions, a typical ``store`` script would look this way:

.. sourcecode:: py

    #!/usr/bin/python

    import ram.unitlib
    from ram.formats import ini

    if __name__ == '__main__':
        config = ram.unitlib.Config()

        try:
            target = ini.cfgopen('/path/to/config.ini', 'section', readonly=False)
            target['option'] = config['option']
            target.sync()
        except IOError as e:
            ram.unitlib.Failed("Cannot open system configuration file: %s" % e)

Different ram units can act in the different configuration sections of the same service configuration file.
As a result, ``try``/``catch`` construct is copied and pasted multiple times in error-prone approach.

Current release introduces context-manager semantics for external config formats such as ini- or env-files.
In addition to that, ``ConfigOpener`` objects are introduced to conveniently utilize context-manager semantics:

.. sourcecode:: py

    #!/usr/bin/python

    import ram.unitlib

    from ram.formats import ini
    from ram.formats import ConfigOpener

    if __name__ == '__main__':
        config = ram.unitlib.Config()

        ini_conf = ConfigOpener(ini.cfgopen, 'system', '/path/to/config.ini')

        with ini_conf('section', readonly=False) as target:
            target['option'] = config['option']

In the example above the ``ConfigOpener`` object is created using ``ini.cfgopen`` as a method to open the file.
The second parameter set to ``'system'`` is used as a short description of the config file. It is used in error messages
generated by ``ConfigOpener``. The third parameter points to the location of the config file in the filesystem. Instance
of the ``ConfigOpener`` object is used as a function producing context manager, its parameters are passed to the ``cfgopen``
method. Once the ``with`` statement completes successfully, the ``sync()`` method of the config object is called.

It is recommended to move the ``ConfigOpener`` object creation to a separate library unit to reuse it from other units.


Data validators
~~~~~~~~~~~~~~~

As in previous releases ram framework provides a way to specifiy validator functions for ``RunEntry`` data fields. But
signature and behaviour of these functions has to be modified. For example, function validating that value is not empty
would look like:

.. sourcecode:: py

    # old way
    def ValidateNonEmpty(title, value):
        if not value:
            return "%s could not be empty\n" % (title,)
        else:
            return ""

Validator functions takes two arguments: title of the field and value to be validated. If no validation errors occur,
function returns empty string. Otherwise function code has to return formatted error message with title considered
as a string.

In current release ram framework takes care of titles and error message formatting. Data validator function takes only
one argument - value to be validated. In case of validation errors function code has to raise ValueError exception
with error message(s) passed as ValueError argument(s). Return value of the function is ignored. But it is a good
practice to return parsed value as a result:

.. sourcecode:: py

    # new way
    def ValidateNonEmpty(value):
        if not value:
            raise ValueError("could not be empty\n")
        else:
            return value


Using shell scripts as actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is recommended to use Shell scripts instead of Python scripts for some unit actions. For example the ``apply``
scripts are usually better expressed in Shell terms because their intention is to check existance and timestamps
of various files and run set of shell commands to restart services. A Python script would be overcomplicated for
this task. Moreover, Shell script can be used to implement the ``store`` script in case there is no suitable parser or
serializer available for a config file format the unit is operating on, but configs can be roughly edited using ``sed``.

The current version of ram framework allows accessing the unit storage db in read-only mode from the same unit Shell
scripts using the following semantics:

.. sourcecode:: sh

    #!/bin/sh

    option=`ram print - option`

In addition to the special ``print`` semantics, this release is distributed with two Shell libraries to reuse in unit scripts:

``/usr/share/ram/ram.functions``
   It is recommended to source this library from every shell unit script. ``ram.functions`` handles special
   environment variables set by ram framework, i.e. turns on shell xtrace if the ram ``debug`` option is set.

``/usr/share/ram/srv.functions``
   Provides set of functions to manage system services and firstboot scripts.
