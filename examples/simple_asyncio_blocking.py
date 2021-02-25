#!/usr/bin/env python

import asyncio
import logging

import uhid


async def main():
    device = uhid.UHIDDevice(
        0x9999, 0x9999, 'Test Device', [
            # Generic mouse report descriptor
            0x05, 0x01,  # Usage Page (Generic Desktop)        0
            0x09, 0x02,  # Usage (Mouse)                       2
            0xa1, 0x01,  # Collection (Application)            4
            0x09, 0x02,  # .Usage (Mouse)                      6
            0xa1, 0x02,  # .Collection (Logical)               8
            0x09, 0x01,  # ..Usage (Pointer)                   10
            0xa1, 0x00,  # ..Collection (Physical)             12
            0x05, 0x09,  # ...Usage Page (Button)              14
            0x19, 0x01,  # ...Usage Minimum (1)                16
            0x29, 0x03,  # ...Usage Maximum (3)                18
            0x15, 0x00,  # ...Logical Minimum (0)              20
            0x25, 0x01,  # ...Logical Maximum (1)              22
            0x75, 0x01,  # ...Report Size (1)                  24
            0x95, 0x03,  # ...Report Count (3)                 26
            0x81, 0x02,  # ...Input (Data,Var,Abs)             28
            0x75, 0x05,  # ...Report Size (5)                  30
            0x95, 0x01,  # ...Report Count (1)                 32
            0x81, 0x03,  # ...Input (Cnst,Var,Abs)             34
            0x05, 0x01,  # ...Usage Page (Generic Desktop)     36
            0x09, 0x30,  # ...Usage (X)                        38
            0x09, 0x31,  # ...Usage (Y)                        40
            0x15, 0x81,  # ...Logical Minimum (-127)           42
            0x25, 0x7f,  # ...Logical Maximum (127)            44
            0x75, 0x08,  # ...Report Size (8)                  46
            0x95, 0x02,  # ...Report Count (2)                 48
            0x81, 0x06,  # ...Input (Data,Var,Rel)             50
            0xc0,        # ..End Collection                    52
            0xc0,        # .End Collection                     53
            0xc0,        # End Collection                      54
        ],
        backend=uhid.AsyncioBlockingUHID,
    )

    await device.wait_for_start_asyncio()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())  # create device
    loop.run_forever()  # run queued dispatch tasks
