#!/usr/bin/python

import ram.process


from fractions import Fraction


fs_types = {
    "ext2": "ext2",
    "ext3": "ext2",
    "ext4": "ext2",
    "vfat": "fat32",
    "swap": "linux-swap",
}


def ConvertSchemeToParted(scheme, available_size):
    to_fit_size = 0
    fixed_size = 0
    for size, _ in scheme:
        if not size:
            raise ValueError("Requirements have zero-size partition.")
        elif size < 0:
            to_fit_size += -size
        else:
            fixed_size += size
    to_fit_multiplier = Fraction(available_size - fixed_size, to_fit_size)

    parted = []
    pt_start = 0
    mk_start = lambda b: str(b/1000**2) + 'MB' if b else "0%"
    mk_end = lambda b, size=available_size: str(b/1000**2) + 'MB' if b < size else "100%"
    for size, fs in scheme:
        if size < 0:
            size = int(-size * to_fit_multiplier)
        parted += [(mk_start(pt_start), mk_end(pt_start + size), fs)]
        pt_start += size

    return parted


def CreatePartitions(dev_path, scheme):
    dev_size = int(ram.process.output('blockdev --getsize64 %s' % dev_path) or 0)
    parted = ConvertSchemeToParted(scheme, dev_size)

    if ram.process.launch('parted -s %s -- mklabel gpt' % dev_path):
        raise RuntimeError("Failed to create disklabel on %s" % dev_path)

    for index, (start, end, fs) in enumerate(parted, 1):
        fs_type = fs_types[fs]
        if ram.process.launch(
            'parted -s %s --align=optimal -- '
            'mkpart primary %s %s %s' % (dev_path, fs_type, start, end)
        ):
            raise RuntimeError("Failed to create partition #%s on %s" % (index, dev_path))

    for index, (start, end, fs) in enumerate(parted, 1):
        mk_prog = "mkswap" if fs == "swap" else ("mkfs.%s" % fs)

        if ram.process.launch(
            '%s %s%s >/dev/null' % (mk_prog, dev_path, index)
        ):
            raise RuntimeError("Failed to format partition #%s on %s" % (index, dev_path))

    return dev_path
