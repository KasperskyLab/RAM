#!/usr/bin/python

import ram.process


class BlockDevice():
    def __init__(self, name, btype, model, size, mount, ro, rm, sect):
        self.name = name
        self.btype = btype
        self.model = model
        self.size = size
        self.mount = mount
        self.ro = ro
        self.rm = rm
        self.sect = sect
        self.subs = []

    def busy(self):
        return self.mount or any([d.mount for d in self.subs])


def GetBlockDevice(name, base=None):
    if not name or name.isalnum():
        name = '/dev/%s' % name

    output = ram.process.output('lsblk -binr -o KNAME,TYPE,MODEL,SIZE,MOUNTPOINT,RO,RM,LOG-SEC %s' % name)

    orig = name
    bdev = None
    for line in output.splitlines():
        name, btype, model, size, mount, ro, rm, sect = line.strip().split(' ')

        size = int(size)
        ro = bool(int(ro))
        rm = bool(int(rm))
        sect = int(sect)

        model = model.decode('unicode_escape').encode('utf8')
        mount = mount.decode('unicode_escape').encode('utf8')

        _dev = BlockDevice(name, btype, model, size, mount, ro, rm, sect)

        if not bdev:
            bdev = _dev
        else:
            bdev.subs += [_dev]

    return bdev


def GetBlockDeviceList(btype_list=None):
    if not btype_list:
        btype_list = []

    output = ram.process.output('lsblk -nd -o KNAME')

    blks = {}
    for line in output.splitlines():
        name = '/dev/' + line.strip()
        bdev = GetBlockDevice(name)
        if btype_list and bdev.btype in btype_list:
            blks[name] = bdev

    return blks
