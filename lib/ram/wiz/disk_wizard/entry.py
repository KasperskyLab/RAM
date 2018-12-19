#!/usr/bin/python

import ram.context

with ram.context(__name__):
    from wiz.disk_choice.entry import RunSelectDiskDrive
    from .utils import CreatePartitions


class RunMkPartDiskDrive(RunSelectDiskDrive):
    def __init__(self, scheme, text=None, dev_path=None, itemExit=None):
        self.scheme = scheme
        size = sum(abs(size) for size, fs in self.scheme)

        super(RunMkPartDiskDrive, self).__init__(size, text=text, dev_path=dev_path, itemExit=itemExit)

    def select_fn(self, dev_path):
        dev_path = super(RunMkPartDiskDrive, self).select_fn(dev_path)

        try:
            return CreatePartitions(dev_path, self.scheme) if dev_path else None
        except Exception as e:
            return ram.widgets.ShowError(
                "Errors during partitioning", str(e)
            )
