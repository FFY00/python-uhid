import asyncio
import os

import pytest

import uhid

from . import find_hidraw


@pytest.mark.timeout(1)
@pytest.mark.asyncio
async def test_create(basic_mouse_rdesc):
    device = uhid.UHIDDevice(0x1234, 0x4321, 'Dummy Mouse', basic_mouse_rdesc, backend=uhid.AsyncioBlockingUHID)

    await device.wait_for_start_asyncio()

    hidraw = find_hidraw(device)

    assert hidraw.info == (device.bus.value, device.vid, device.pid) == (uhid.Bus.USB.value, 0x1234, 0x4321)
    assert hidraw.name == device.name == 'Dummy Mouse'
    assert hidraw.phys == device.physical_name == f'UHIDDevice/{device.unique_name}'
    assert hidraw.report_descriptor == device.report_descriptor == basic_mouse_rdesc
    assert device.version == 0
    assert device.country == 0

    device.destroy()


@pytest.fixture()
@pytest.mark.asyncio
async def vendor_device(vendor_rdesc):
    device = uhid.UHIDDevice(0x4321, 0x1234, 'Dummy Mouse', vendor_rdesc, backend=uhid.AsyncioBlockingUHID)
    await device.wait_for_start_asyncio()
    yield device
    device.destroy()


@pytest.fixture()
@pytest.mark.asyncio
def vendor_hidraw(vendor_device):
    return find_hidraw(vendor_device)


@pytest.mark.asyncio
async def test_output(vendor_device, vendor_hidraw):
    data = [0, 1, 2, 3, 4, 5, 6, 7]
    received = []

    def receive_output(data, report_type):
        received.append(data)

    vendor_device.receive_output = receive_output

    os.write(vendor_hidraw.fd, bytes(data))
    os.write(vendor_hidraw.fd, bytes(list(reversed(data))))

    await asyncio.sleep(0.1)  # give some time for the events to be dispatched

    assert received == [data, list(reversed(data))]
