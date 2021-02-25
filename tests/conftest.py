import pytest


@pytest.fixture
def basic_mouse_rdesc():
    return [
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
    ]


@pytest.fixture
def vendor_rdesc():
    return [
        # Vendor page report descriptor
        0x06, 0x00, 0xff,   # Usage Page (Vendor Page)
        0x09, 0x00,         # Usage (Vendor Usage 0)
        0xa1, 0x01,         # Collection (Application)
        0x85, 0x20,	        # .Report ID (0x20)
        0x75, 0x08,	        # .Report Size (8)
        0x95, 0x08,	        # .Report Count (8)
        0x15, 0x00,	        # .Logical Minimum (0)
        0x26, 0xff, 0x00,   # .Logical Maximum (255)
        0x09, 0x00,	        # .Usage (Vendor Usage 0)
        0x81, 0x00,	        # .Input (Data,Arr,Abs)
        0x09, 0x00,	        # .Usage (Vendor Usage 0)
        0x91, 0x00,	        # .Outpur (Data,Arr,Abs)
        0xc0,               # End Collection
    ]
