#!/usr/bin/python

import ram.context
import ram.widgets


with ram.context(__name__):
    from wiz.utils import BuildBytes
    from wiz.entry import RunDictIndex

from utils import TryDevice, IterDevices


class RunSelectDiskDrive(object):
    def __init__(self, size, text=None, dev_path=None, itemExit=None):
        self.size = size or 0
        self.text = text
        self.dev_path = dev_path
        self.itemExit = itemExit

        if self.text is None:
            self.text="Select disk drive for system installation.\n\n"

        if self.itemExit is None:
            self.itemExit="Cancel installation ..."

        self.st_cache = {}
        self.dev_list = []

    def format_fn(self, dev_path):
        dev_stat, dev_errs, dev_wrns = self.st_cache[dev_path]

        dev_size = BuildBytes(dev_stat.size, precise=1, bsuffix=True)
        dev_errs = "!" if dev_errs else " "

        return "%s Disk: %8s %8s %s" % (dev_errs, dev_path, dev_size, dev_stat.model)

    def select_fn(self, dev_path, ask_wrns=True):
        dev_info, dev_errs, dev_wrns = self.st_cache[dev_path]

        if dev_errs:
            return ram.widgets.ShowError(
                "Error",
                "Device `%s` cannot be used:\n\n" % dev_path + "\n\n".join(' - ' + _ for _ in dev_errs),
            )
        elif ask_wrns and not ram.widgets.AskViaButtons(
            "Warning",
            "Would you like to use device `%s`?\n\n" % dev_path+ "\n\n".join(' - ' + _ for _ in dev_wrns),
        ):
            return
        else:
            return dev_path

    def values_fn(self, dev_path=None):
        dev_list = self.dev_list if not dev_path else [dev_path]

        for dev_path in dev_list:
            self.st_cache[dev_path] = TryDevice(dev_path, self.size, False)

        return dev_list

    def __call__(self):
        self.dev_list = sorted(IterDevices())

        if not self.dev_list:
            return ram.widgets.ShowError(
                "Error",
                "Cannot find any disk device."
            )
        elif not self.dev_path:
            return RunDictIndex(
                header="Select device",
                text=self.text + (
                    "Devices marked with `!` sign are not suitable.\n"
                ) + (
                    "Disk size requirements: %s.\n" % BuildBytes(self.size, precise=1, bsuffix=True) if self.size else ""
                ),
                title="",
                values_fn=self.values_fn,
                format_fn=self.format_fn,
                modify_fn=self.select_fn,
                itemExit=self.itemExit,
            )
        elif not self.dev_path in self.dev_list:
            return ram.widgets.ShowError(
                "Error",
                "Cannot find disk device `%s`." % self.dev_path
            )
        else:
            return self.select_fn(self.values_fn(self.dev_path).pop())
