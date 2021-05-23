from typing import Optional

from pydantic import BaseModel

from models import DeviceTypeEnum, DeviceConnectionOption, DeviceStatusEnum


class PyDevice(BaseModel):
    hostname: Optional[str]
    address: str
    mac: Optional[str]
    type: DeviceTypeEnum
    os: str
    status: DeviceStatusEnum
    connection_options: list[DeviceConnectionOption]
    connected_with: list[int]
    raw_scan_data: dict

    class Config:
        orm_mode = True
        use_enum_values = True


class PyDeviceCreateIn(BaseModel):
    agent_key = str
    hostname: Optional[str]
    address: str
    mac: Optional[str]
    type: Optional[DeviceTypeEnum]
    os: Optional[str]
    status: Optional[DeviceStatusEnum]
    connection_options: list[DeviceConnectionOption]
    connected_with: list[int]
    raw_scan_data: dict

    class Config:
        use_enum_values = True


class PyDeviceUpdateIn(BaseModel):
    type: DeviceTypeEnum

    class Config:
        use_enum_values = True
