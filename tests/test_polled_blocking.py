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
