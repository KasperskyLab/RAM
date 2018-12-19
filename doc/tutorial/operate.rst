
Issuing commands to `ram` units
-------------------------------

There could be a lot of different `units` available on the system.
And `the ram framework` aims to provide unified interface to interact with these `units`.
As you can see some of the `units` shown in the output of ``ram index`` command has `*`-mark.
Asterisk indicates that given `unit` provides menu-based configuration interface.
To run configuration menu just type:

.. sourcecode:: console

    # ram setup <unit-name>

Once functionality domain has been configured changes has to be applied to running services. To do this:

.. sourcecode:: console

    # ram apply <unit-name>
