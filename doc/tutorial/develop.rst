

How to create own unit
----------------------

To start development of ram units, the following preparation steps should be done:

 * Create top level library directory and it's path to ram search path list:

   .. sourcecode:: console

       # mkdir -p <top-level>
       # echo <top-level> > /etc/ram/<library-name>

 * Set trace mode to see executed commands and their exit codes:

   .. sourcecode:: console

       # # enable trace-mode
       # ram tweak trace on

       # # disable trace-mode
       # ram tweak trace off

 * Set debug mode to see full tracebacks of ram framework exceptions:

   .. sourcecode:: console

       # # enable debug-mode
       # ram tweak debug on

       # # disable debug-mode
       # ram tweak debug off

 * Create blank unit:

   .. sourcecode:: console

       # ram-mkunit <top-level>/<unit-name>


The latter command creates directory for the unit source code and creates empty files for all standard entry points:

``about``
    Text file with unit description, first line will be used in the output of the ``index`` command.

``query``
    This script collects configuration data from the service configuration file.

``input``
    This script uses framework's calls to interact with a user in a wizard way.

``store``
    This script updates configuration data in the service configuration file.

``apply``
    This script restarts services affected by changed configuration file.


As a result, unit will be available as `<unit-name>` for any ram command, for example:

    .. sourcecode:: console

        # ram print <unit-name>
