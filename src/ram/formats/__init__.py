#!/usr/bin/python

from functools import wraps
from collections import MutableMapping

from ram.osutils import from_exception


# StringDict class is provided to serve access
# to configuration storages where empty keys are
# equivalent of missing keys. Moreover this class
# provides conformance with dictionary semantic
# for sibling classes.

class StringDict(MutableMapping):
    def __init__(self, dict_obj, delblank=True):
        self.dict_obj = dict_obj
        self.delblank = delblank

    def __getitem__(self, key):
        if not isinstance(key, basestring):
            raise TypeError("keys and values of this mapping should be strings.")
        try:
            return self.dict_obj[key]
        except KeyError:
            return ''

    def __setitem__(self, key, value):
        if not isinstance(key, basestring) or not isinstance(value, basestring):
            raise TypeError("keys and values of this mapping should be strings.")
        if not value and self.delblank:
            del self[key]
        else:
            self.dict_obj[key] = value

    def __delitem__(self, key):
        if not isinstance(key, basestring):
            raise TypeError("keys and values of this mapping should be strings.")
        try:
            del self.dict_obj[key]
        except KeyError:
            pass

    def __iter__(self):
        try:
            iterkeys = iter(self.dict_obj)
        except TypeError:
            iterkeys = iter(self.dict_obj.keys())

        for key in iterkeys:
            yield key

    def __contains__(self, key):
        return key in list(iter(self))

    def __len__(self):
        return len(list(iter(self)))

    def copy(self):
        try:
            return self.dict_obj.copy()
        except (AttributeError, TypeError):
            return dict(self)


# SyncedDict class is provided to track modifications
# in underlying settings storage engines. To track
# changes objects holds a copy of last synchronized
# settings and checks for exclusive intersection
# between current data and copy.

class SyncedDict(StringDict):
    def __init__(self, readonly, delblank, baresync=False):
        self.readonly = readonly
        super(SyncedDict, self).__init__(self.__read__(), delblank)
        self.dictcopy = self.copy()
        self.baresync = baresync
        self._suspend = False

    def modified(self):
        return bool(set(self.dictcopy.iteritems()) ^ set(self.iteritems()))

    def __read__(self):
        raise NotImplementedError()

    def __sync__(self):
        raise NotImplementedError()

    def sync(self):
        if self.readonly:
            raise IOError("attempting to store readonly config.")
        if self.modified():
            self.__sync__()
            self.dictcopy = self.copy()

    def undo(self):
        self.clear()
        self.update(self.dictcopy)

    def __setitem__(self, key, value):
        super(SyncedDict, self).__setitem__(key, value)
        if self.baresync and not self._suspend and not self.readonly:
            self.sync()

    def __delitem__(self, key):
        super(SyncedDict, self).__delitem__(key)
        if self.baresync and not self._suspend and not self.readonly:
            self.sync()

    def __enter__(self):
        if self._suspend:
            raise IOError("attempting to lock already locked config.")
        else:
            self._suspend = True
            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type or exc_val or exc_tb:
            self.undo()

        self._suspend = False
        if not self.readonly:
            self.sync()


# ConfigDict and ConfigItem classes are provided to
# serve qualified access to entries in settings storage.
# ConfigDict is a general wrapper over StringDict which
# returns ConfigItem entities on access.
# On its behalf ConfigItem is generally acting as a regular
# string. However it makes possible to access other entries
# in original storage that have ConfigItem prefixed key.
#
# See usage example in the __main__ section below.


class ConfigDict(SyncedDict):
    def use(self):
        return ConfigItem(self, '', self[''])


class ConfigItem(str):
    def __new__(self, config, key, value):
        self = str.__new__(self, value)
        self.config = config
        self.prefix = key.strip('.')
        return self

    def __mkindex(self, key):
        key = self.prefix + '.' + key.lstrip('.')
        return key.strip('.')

    def __getitem__(self, key):
        if isinstance(key, basestring):
            index = self.__mkindex(key)
            value = self.config[index]
            return ConfigItem(self.config, index, value)
        else:
            return str.__getitem__(self, key)

    def __setitem__(self, key, value):
        if isinstance(key, basestring):
            self.config[self.__mkindex(key)] = value
        else:
            str.__setitem__(self, key, value)

    def __delitem__(self, key):
        if isinstance(key, basestring):
            sub = self.__getitem__(key)
            for subkey in sub.keys():
                sub.__delitem__(subkey)
            del self.config[self.__mkindex(key)]
        else:
            str.__delitem__(self, key)

    def iterkeys(self):
        seen = set()

        for key in self.config:
            if not key.startswith(self.prefix):
                continue

            subkey, _, _ = key[len(self.prefix):].lstrip('.').partition('.')
            if not subkey:
                continue

            if not subkey in seen:
                seen.add(subkey)
                yield subkey.lstrip('.')

    def keys(self):
        return list(self.iterkeys())

    def itervalues(self):
        for key in self.iterkeys():
            yield self.config[self.__mkindex(key)]

    def values(self):
        return list(self.itervalues())

    def iteritems(self):
        for key in self.iterkeys():
            yield (key, self.config[self.__mkindex(key)])

    def items(self):
        return list(self.iteritems())


def configopen(_cfgopen, mergepath=True, storagedb=False):
    @wraps(_cfgopen)
    def _opener(dirname, section=None, readonly=True, **kwargs):
        if mergepath:
            dirname = '%s/%s' % (dirname, section) if section else dirname
            section = ""
        elif not section:
            raise ValueError("Section name required to open config.")

        return _cfgopen(dirname, section, readonly, **kwargs)
    return _opener


class ConfigOpener(object):
    def __init__(self, cfgopen, filekey, filepath):
        self.cfgopen = cfgopen
        self.filekey = filekey
        self.filepath = filepath

    def __call__(self, *args, **kwargs):
        try:
            return self.cfgopen(self.filepath, *args, **kwargs)
        except IOError as err:
            raise from_exception(
                "Unable to open `%s` configuration: %s" % (self.filekey, err)
            )


if __name__ == '__main__':

    data = {
        "master.data.v1": "data1",
        "master.data.v2": "data2",
        "worker.address": "http:",
        "worker": "johny",
    }

    config = ConfigDict(data)

    print config['worker']
    print config['worker.address']
    print config['worker']['address']

    config['worker'] = 'nancy'

    for sym in config['worker']:
        print sym,
    print

    config['worker'] = config['worker'].upper()

    for key in config['master'].iterkeys():
        print key, config['master'][key]

    config['master']['access']['key'] = 'qwerty'
    print dict(config)
