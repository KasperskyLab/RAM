#!/usr/bin/python

import lsblk


def TryDevice(dev_path, size, subs):
    dev_errs = []
    dev_warn = []

    dev = lsblk.GetBlockDevice(dev_path)

    if dev.btype != 'disk':
        dev_errs.append("Cannot operate on disks of type: %s." % dev.btype)

    if dev.ro:
        dev_errs.append("The device is read-only.")

    if dev.busy():
        dev_errs.append("Cannot operate on disks in use.")

    if size and dev.size < size:
        dev_errs.append("Disk size doesn't fit requirements.")

    if not dev.subs:
        pass
    elif subs:
        dev_errs.append("Disk has %s partitions." % len(dev.subs))
    else:
        dev_warn.append("Disk has %s partitions." % len(dev.subs))

    return dev, dev_errs, dev_warn


def IterDevices(btype='disk'):
    btype_list = btype.split(',') if btype else []
    return lsblk.GetBlockDeviceList(btype_list).iterkeys()
