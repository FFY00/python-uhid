import pytest
import trio

import uhid

from . import find_hidraw


@pytest.mark.trio
async def test_create(basic_mouse_rdesc):
    with trio.fail_after(3):
        device = await uhid.AsyncUHIDDevice.new(0x1234, 0x4321, 'Dummy Mouse', basic_mouse_rdesc, backend=uhid.TrioUHID)

    hidraw = find_hidraw(device)

    assert hidraw.info == (device.bus.value, device.vid, device.pid) == (uhid.Bus.USB.value, 0x1234, 0x4321)
    assert hidraw.name == device.name == 'Dummy Mouse'
    assert hidraw.phys == device.physical_name == f'AsyncUHIDDevice/{device.unique_name}'[:63]
    assert hidraw.report_descriptor == device.report_descriptor == basic_mouse_rdesc
    assert device.version == 0
    assert device.country == 0

    await device.destroy()
