``apply`` service
=================

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
