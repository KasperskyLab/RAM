#!/usr/bin/python

import ram

flavor = ram.query('sys.distrib')['base']

if flavor == 'redhat':
    from ifcfg_redhat import *
else:
    raise NotImplementedError()
