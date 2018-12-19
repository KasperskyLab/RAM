
Getting in touch with `ram`
---------------------------

Crucial part of `the ram framework` is the `ram` command-line utility.
It's interface reuses idea of subcommands known to every user of popular package managers (i.e. ``apt-get`` of ``yum``).
To get brief hint about basic `ram` commands just type ``ram`` or ``ram usage``:

.. sourcecode:: console

    # ram usage
    the ram framework v0.4.4

      To see list of available services:

        $ ram proto

      To see help for a given service:

        $ ram usage <service>

      To see list of all indexed units:

        $ ram index


As shown in the output command ``ram proto`` could be used to get list of all available commands (internally called services).
Every available command is followed by short command description:

.. sourcecode:: console

    # ram proto
    about           . shows description for the unit
    apply           * applies configuration to environment
    cache           * (deprecated) only for compatibility
    debug           * (experimental) use python to import namepath
    files           . shows file list managed by the unit
    index           . shows list of indexed units
    input           * runs dialogs to interact with user
    param           . shows parameter list for the unit
    print           . shows configuration from storage
    probe           * probes service in the environment
    purge           * purges configuration from storage
    query           * queries configuration from files
    reset           * parses configuration from input
    setup           * use unit to configure environment
    store           * stores configuration to files
    proto             shows list of available services
    tweak             shows or edits internal parameters
    usage             shows usage messages
    watch           . watches events sensible for the unit
    which           . shows file paths of unit files


To get usage examples for any of the commands just type ``ram usage <command>``:

.. sourcecode:: console

    # ram usage index
    index: shows list of indexed units

      To see list of all indexed units:

        $ ram index

      To see list of all units at namepath:

        $ ram index <namepath>


As you can see in the output of ``ram proto`` most of `ram` commands are marked with either `*` or `.` mark.
Commands without any mark should be considered as generic (i.e. ``ram proto`` or ``ram usage``).
On the other hand presence of mark indicates that given command operates on `units`.
From the user perspective every `unit` is a backend to configure particular functionality domain.
For example `ifconfig` unit from standard library provide a way to configure network interfaces and
`timezone` unit serves for timezone selection.

To get the list of all available units just type the ``ram index`` command:

.. sourcecode:: console

    # ram index
    account                  ---- Account configuration-related functions.
    adminwiz                 *..- Create new system user and set password.
    datetime                 *... Configure system clock.
    diskwiz                  *..- Disk partitioning.
    eulawiz                  *--- Find suitable EULA files and ask user to agree on terms.
    generic                  ---- Generic functions for units.
    hostname                 *... Configure hostname.
    ifconfig                 *... Network interface configuration.
    internet                 ---- Internet URL manipulation functions for units.
    logview                  *--- View system logs using less.
    network                  ---- Network configuration-related functions for units.
    pipecat                  *--- Generic unit to display pipe data transfer progress.
    resolver                 *... Configure DNS resolver.
    routing                  *... Configure gateway and routes.
    timewiz                  *... Generic time configuration.
    timezone                 *..- Configure timezone for the machine.
