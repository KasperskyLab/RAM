
Example unit
------------

Below is the source code for the unit designed to edit arguments system cron daemon is launched with.

about:

.. sourcecode:: none

    Configure cron daemon

query:

.. sourcecode:: python

    #!/usr/bin/python

    import ram.unitlib

    from ram.formats import env

    if __name__ == '__main__':
        config = ram.unitlib.Config()

        with env.cfgopen('/etc/sysconfig/crond', readonly=True) as source:
            config['options'] = source['CRONDARGS']

input:

.. sourcecode:: python

    #!/usr/bin/python

    import ram.unitlib
    import ram.widgets

    if __name__ == '__main__':
        config = ram.unitlib.Config()

        config['options'], = ram.widgets.RunEntry(
            "Cron daemon arguments",
            "",
            [
                ("Arguments", config['options'], None),
            ],
            allowCancel=True,
            supplySaved=True,
        )

store:

.. sourcecode:: python

    #!/usr/bin/python

    import ram.unitlib

    from ram.formats import env

    if __name__ == '__main__':
        config = ram.unitlib.Config()

        with env.cfgopen('/etc/sysconfig/crond', readonly=False) as target:
            target['CRONDARGS'] = config['options']

apply:

.. sourcecode:: sh

    #!/bin/sh

    . /usr/share/ram/ram.functions

    if [ -f "/var/lock/subsys/crond" -a "/var/lock/subsys/crond" -ot "/etc/sysconfig/crond" ]; then
        service crond condrestart
    fi

