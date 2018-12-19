#!/usr/bin/python

from distutils.core import setup

import os

from ram import __version__, __release__


if __name__ == '__main__':
    setup(
        name='ram',
        version=__version__,
        description='the ram framework',
        author='Roman Valov',
        license='MIT',
        packages=['ram', 'ram.classes', 'ram.service', 'ram.formats'],
        data_files=(
            [
                ('/usr/share/ram', ['share/srv.functions', 'share/ram.functions']),
                ('/etc/bash_completion.d', ['share/bash-completion/ram']),
            ]
        ),
        scripts=['bin/ram', 'bin/ram-symbols'],
        classifiers=(
            'Development Status :: 3 - Alpha',
            'Environment :: Console :: Newt',
            'Intended Audience :: Developers',
            'License :: MIT',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Topic :: Software Development :: Libraries :: Application Frameworks',
            'Topic :: System :: Installation/Setup',
        )
    )
