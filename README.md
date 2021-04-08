# python-uhid

![checks](https://github.com/FFY00/python-uhid/workflows/checks/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/python-uhid/badge/?version=latest)](https://python-uhid.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/uhid.svg)](https://pypi.org/project/uhid/)

Pure Python typed UHID wrapper.

Supported backends:
  - Blocking IO + epoll
    - Uses the epoll API to watch the UHID file descriptor for input events
  - asyncio blocking IO
    - Uses asyncio reader and writer tasks
  - trio
    - Async API built on top of trio

See the [examples folder](https://github.com/FFY00/python-uhid/tree/master/examples) for example snippets of each backend.

UHID is a Linux API to create virtual HID devices.
See the [official UHID documentation](https://www.kernel.org/doc/Documentation/hid/uhid.txt).
