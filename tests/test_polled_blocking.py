import os
import threading
import time

import pytest

import uhid

from . import find_hidraw


@pytest.mark.timeout(1)
def test_create(basic_mouse_rdesc):
    device = uhid.UHIDDevice(0x1234, 0x4321, 'Dummy Mouse', basic_mouse_rdesc, backend=uhid.PolledBlockingUHID)

    hidraw = find_hidraw(device)

    assert hidraw.info == (device.bus.value, device.vid, device.pid) == (uhid.Bus.USB.value, 0x1234, 0x4321)
    assert hidraw.name == device.name == 'Dummy Mouse'
    assert hidraw.phys == device.physical_name == f'UHIDDevice/{device.unique_name}'
    assert hidraw.report_descriptor == device.report_descriptor == basic_mouse_rdesc
    assert device.version == 0
    assert device.country == 0

    device.destroy()


@pytest.fixture()
def vendor_device(vendor_rdesc):
    device = uhid.UHIDDevice(0x4321, 0x1234, 'Dummy Mouse', vendor_rdesc, backend=uhid.PolledBlockingUHID)
    device.wait_for_start()

    stop_dispatch = threading.Event()
    dispatch_thread = threading.Thread(target=device.dispatch, args=(stop_dispatch,))
    dispatch_thread.start()

    try:
        yield device
    finally:
        stop_dispatch.set()
        device.destroy()


@pytest.fixture()
def vendor_hidraw(vendor_device):
    return find_hidraw(vendor_device)


def test_output(vendor_device, vendor_hidraw):
    data = [0, 1, 2, 3, 4, 5, 6, 7]
    received = []

    def receive_output(data, report_type):
        received.append(data)

    vendor_device.receive_output = receive_output

    os.write(vendor_hidraw.fd, bytes(data))
    os.write(vendor_hidraw.fd, bytes(list(reversed(data))))

    time.sleep(0.1)  # give some time for the events to be dispatched

    assert received == [data, list(reversed(data))]
