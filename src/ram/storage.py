#!/usr/bin/python

import atexit

import ram.channel
import ram.symbols

from ram.osutils import getenv


class Storage(object):
    @staticmethod
    def _query(namepath):
        import ram.symbols

        data = ram.symbols()
        def _flush(data=data):
            ram.symbols.send(data)

        atexit.register(_flush)
        return data

    @staticmethod
    def _input(namepath):
        data = ram.query(namepath)
        def _flush(data=data):
            ram.store(namepath, input=data)

        atexit.register(_flush)
        return data

    @staticmethod
    def _store(namepath):
        import ram.symbols

        return ram.symbols.recv()

    @staticmethod
    def conf(namepath):
        confmode = getenv('RAMMODE')
        if confmode == 'input':
            return Storage._input(namepath)
        elif confmode == 'query':
            return Storage._query(namepath)
        elif confmode == 'store':
            return Storage._store(namepath)
        else:
            raise EnvironmentError("Unsupported mode of operation for `Config` interface.")
