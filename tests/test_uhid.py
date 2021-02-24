import asyncio
import os

import ioctl.hidraw
import pytest
import trio

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


@pytest.mark.timeout(1)
def test_create_polled_blocking(basic_mouse_rdesc):
    device = uhid.UHIDDevice(0x1234, 0x4321, 'Dummy Mouse', basic_mouse_rdesc, backend=uhid.PolledBlockingUHID)

    hidraw = find_hidraw(device)
    print(hidraw)

    assert hidraw.info == (device.bus.value, device.vid, device.pid) == (uhid.Bus.USB.value, 0x1234, 0x4321)
    assert hidraw.name == device.name == 'Dummy Mouse'
    assert hidraw.phys == device.physical_name == f'UHIDDevice/{device.unique_name}'
    assert hidraw.report_descriptor == device.report_descriptor == basic_mouse_rdesc
    assert device.version == 0
    assert device.country == 0


@pytest.mark.asyncio
@pytest.mark.timeout(1)
async def test_create_asyncio_blocking(basic_mouse_rdesc):
    device = uhid.UHIDDevice(0x1234, 0x4321, 'Dummy Mouse', basic_mouse_rdesc, backend=uhid.AsyncioBlockingUHID)

    await asyncio.sleep(0.1)

    hidraw = find_hidraw(device)
    print(hidraw)

    assert hidraw.info == (device.bus.value, device.vid, device.pid) == (uhid.Bus.USB.value, 0x1234, 0x4321)
    assert hidraw.name == device.name == 'Dummy Mouse'
    assert hidraw.phys == device.physical_name == f'UHIDDevice/{device.unique_name}'
    assert hidraw.report_descriptor == device.report_descriptor == basic_mouse_rdesc
    assert device.version == 0
    assert device.country == 0


@pytest.mark.trio
async def test_create_trio(basic_mouse_rdesc):
    with trio.fail_after(3):
        device = await uhid.AsyncUHIDDevice.new(0x1234, 0x4321, 'Dummy Mouse', basic_mouse_rdesc, backend=uhid.TrioUHID)

    hidraw = find_hidraw(device)

    assert hidraw.info == (device.bus.value, device.vid, device.pid) == (uhid.Bus.USB.value, 0x1234, 0x4321)
    assert hidraw.name == device.name == 'Dummy Mouse'
    assert hidraw.phys == device.physical_name == f'AsyncUHIDDevice/{device.unique_name}'[:63]
    assert hidraw.report_descriptor == device.report_descriptor == basic_mouse_rdesc
    assert device.version == 0
    assert device.country == 0
