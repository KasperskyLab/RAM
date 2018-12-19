``tweak`` service
=================


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
