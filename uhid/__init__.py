# SPDX-License-Identifier: MIT

import ctypes
import enum
import logging
import os
import os.path
import uuid

from typing import Optional, Sequence

import caio


BUS_PCI = 0x01
BUS_ISAPNP = 0x02
BUS_USB = 0x03
BUS_HIL = 0x04
BUS_BLUETOOTH = 0x05
BUS_VIRTUAL = 0x06

_HID_MAX_DESCRIPTOR_SIZE = 4096
_UHID_DATA_MAX = 4096


class _EventType(enum.Enum):
    # UHID_LEGACY_CREATE = 0
    UHID_DESTROY = 1
    UHID_START = 2
    UHID_STOP = 3
    UHID_OPEN = 4
    UHID_CLOSE = 5
    UHID_OUTPUT = 6
    # UHID_LEGACY_OUTPUT_EV = 7
    # UHID_LEGACY_INPUT = 8
    UHID_GET_REPORT = 9
    UHID_GET_REPORT_REPLY = 10
    UHID_CREATE2 = 11
    UHID_INPUT2 = 12
    UHID_SET_REPORT = 13
    UHID_SET_REPORT_REPLY = 14


class _DevFlag(enum.Enum):
    UHID_DEV_NUMBERED_FEATURE_REPORTS = 1 << 0
    UHID_DEV_NUMBERED_OUTPUT_REPORTS = 1 << 1
    UHID_DEV_NUMBERED_INPUT_REPORTS = 1 << 2


class _ReportType(enum.Enum):
    UHID_FEATURE_REPORT = 0
    UHID_OUTPUT_REPORT = 1
    UHID_INPUT_REPORT = 2


# _LegacyEventType


class _Create2Req(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('name', ctypes.c_char * 128),
        ('phys', ctypes.c_char * 64),
        ('uniq', ctypes.c_char * 64),
        ('rd_size', ctypes.c_uint16),
        ('bus', ctypes.c_uint16),
        ('vendor', ctypes.c_uint32),
        ('product', ctypes.c_uint32),
        ('version', ctypes.c_uint32),
        ('country', ctypes.c_uint32),
        ('rd_data', ctypes.c_uint8 * _HID_MAX_DESCRIPTOR_SIZE),
    ]


class _StartReq(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('dev_flags', ctypes.c_uint64),
    ]


class _Input2Req(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('size', ctypes.c_uint16),
        ('data', ctypes.c_uint8 * _UHID_DATA_MAX),
    ]


class _OutputReq(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('data', ctypes.c_uint8 * _UHID_DATA_MAX),
        ('size', ctypes.c_uint16),
        ('rtype', ctypes.c_uint8),
    ]


class _GetReportReq(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('id', ctypes.c_uint32),
        ('rnum', ctypes.c_uint8),
        ('rtype', ctypes.c_uint8),
    ]


class _GetReportReplyReq(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('id', ctypes.c_uint32),
        ('err', ctypes.c_uint16),
        ('size', ctypes.c_uint16),
        ('data', ctypes.c_uint8 * _UHID_DATA_MAX),
    ]


class _SetReportReq(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('id', ctypes.c_uint64),
        ('rnum', ctypes.c_uint8),
        ('rtype', ctypes.c_uint8),
        ('size', ctypes.c_uint16),
        ('data', ctypes.c_uint8 * _UHID_DATA_MAX),
    ]


class _SetReportReplyReq(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('id', ctypes.c_uint32),
        ('err', ctypes.c_uint16),
    ]


class _U(ctypes.Union):
    _fields_ = [
        ('output', _OutputReq),
        ('get_report', _GetReportReq),
        ('get_report_reply', _GetReportReplyReq),
        ('create2', _Create2Req),
        ('input2', _Input2Req),
        ('set_report', _SetReportReq),
        ('set_report_reply', _SetReportReplyReq),
        ('start', _StartReq),
    ]


class _Event(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('type', ctypes.c_uint32),
        ('u', _U),
    ]

# _CreateReq, _InputReq, _OutputEvReq, _FeatureReq, _FeatureAnswerReq


class UHIDException(Exception):
    '''
    Exception triggered when interfacing with UHID
    '''


class UHID(object):
    '''
    Low level UHID wrapper
    '''

    def __init__(self) -> None:
        if not os.path.exists('/dev/uhid'):
            raise RuntimeError('UHID is not available (/dev/uhid is missing)')

        self._uhid = os.open('/dev/uhid', os.O_RDWR)
        self._open = False

        self._ctx = caio.AsyncioContext()

        self.__logger = logging.getLogger(self.__class__.__name__)

    async def _send_event(self, event_type: _EventType, data: ctypes.Structure) -> None:
        data_union = _U(**{event_type.name.strip('UHID_').lower(): data})
        event = _Event(event_type.value, data_union)

        n = await self._ctx.write(bytes(data), self._uhid, offset=0)

        if n != ctypes.sizeof(event):
            raise UHIDException(f'Failed to send data ({n} != {ctypes.sizeof(event)})')

    async def create(
        self,
        name: str,
        phys: str,
        uniq: str,
        bus: int,
        vendor: int,
        product: int,
        version: int,
        country: int,
        rd_data: Sequence[int]
    ) -> None:
        if self._open:
            raise UHIDException('This instance already has a device open, it is only possible to open 1 device per instance')

        self.__logger.info('UHID_CREATE2')

        if len(name) > _Create2Req.name.size:
            raise UHIDException(f'UHID_CREATE2: name is too big ({len(name) > _Create2Req.name.size})')

        if len(phys) > _Create2Req.phys.size:
            raise UHIDException(f'UHID_CREATE2: phys is too big ({len(phys) > _Create2Req.phys.size})')

        if len(uniq) > _Create2Req.uniq.size:
            raise UHIDException(f'UHID_CREATE2: uniq is too big ({len(uniq) > _Create2Req.uniq.size})')

        if len(rd_data) > _Create2Req.rd_data.size:
            raise UHIDException(f'UHID_CREATE2: rd_data is too big ({len(rd_data) > _Create2Req.rd_data.size})')

        await self._send_event(_EventType.UHID_CREATE2, _Create2Req(
            name.encode(),
            phys.encode(),
            uniq.encode(),
            len(rd_data),
            bus,
            vendor,
            product,
            version,
            country,
            (ctypes.c_uint8 * _HID_MAX_DESCRIPTOR_SIZE)(*rd_data)
        ))
        self._open = True


class UHIDDevice(object):
    @classmethod
    async def initialize(cls, *args, **kwargs) -> 'UHIDDevice':
        device = cls(*args, **kwargs)
        await device.create()
        return device

    def __init__(
        self,
        vid: int,
        pid: int,
        name: str,
        report_descriptor: Sequence[int],
        *,
        bus: int = BUS_USB,
        physical_name: str = '',
        unique_name: Optional[str] = None,
        version: int = 0,
        country: int = 0,
    ) -> None:
        if not unique_name:
            unique_name = f'{self.__class__.__name__}_{uuid.uuid4()}'

        self._bus = bus
        self._vid = vid
        self._pid = pid
        self._name = name
        self._phys = physical_name
        self._uniq = unique_name
        self._version = version
        self._country = country
        self._rdesc = report_descriptor

        self.__logger = logging.getLogger(self.__class__.__name__)

        self._uhid = UHID()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(vid={self.vid}, pid={self.pid}, name={self.name}, uniq={self.unique_name})'

    @property
    def bus(self) -> int:
        return self._bus

    @property
    def vid(self) -> int:
        return self._vid

    @property
    def pid(self) -> int:
        return self._pid

    @property
    def name(self) -> str:
        return self._name

    @property
    def physical_name(self) -> str:
        return self._phys

    @property
    def unique_name(self) -> str:
        return self._uniq

    @property
    def report_descriptor(self) -> Sequence[int]:
        # lists are mutable, we don't want users to modify our private list :)
        if isinstance(self._rdesc, list):
            return self._rdesc.copy()
        return self._rdesc

    @property
    def version(self) -> int:
        return self._version

    @property
    def country(self) -> int:
        return self._country

    async def create(self) -> None:
        self.__logger.info(f'create {self}')
        await self._uhid.create(
            self._name,
            self._phys,
            self._uniq,
            self._bus,
            self._vid,
            self._pid,
            self._version,
            self._country,
            self._rdesc
        )
