import os

import ioctl.hidraw

import uhid


def find_hidraw(device: uhid.UHIDDevice) -> ioctl.hidraw.Hidraw:
    visited = set()

    while True:
        for node in os.listdir('/dev'):
            if node in visited:  # pragma: no cover
                continue

            visited.update([node])
            if node.startswith('hidraw'):
                hidraw = ioctl.hidraw.Hidraw(f'/dev/{node}')

                if device.unique_name == hidraw.uniq:
                    return hidraw
