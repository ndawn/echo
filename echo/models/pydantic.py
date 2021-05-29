from typing import Optional

from pydantic import BaseModel

from echo.models import DeviceTypeEnum, DeviceConnectionOption


class PyDeleteOut(BaseModel):
    deleted: bool


class PySubnet(BaseModel):
    pk: int
    cidr: str
    gateway_address: str

    class Config:
        orm_mode = True


class PySubnetCreateIn(BaseModel):
    cidr: str
    gateway_address: str


class PyAgentFull(BaseModel):
    pk: int
    address: str
    subnet: PySubnet
    token: str

    class Config:
        orm_mode = True


class PyAgent(BaseModel):
    pk: int
    address: str
    subnet: PySubnet

    class Config:
        orm_mode = True


class PyAgentCreateUpdateIn(BaseModel):
    address: str
    subnet_id: str


class PyDevice(BaseModel):
    pk: int
    subnet: PySubnet
    hostname: Optional[str]
    address: str
    mac: Optional[str]
    type: DeviceTypeEnum
    connection_options: list[DeviceConnectionOption]
    connected_with: list[int]

    class Config:
        orm_mode = True
        use_enum_values = True


class PyDeviceCreateUpdateIn(BaseModel):
    subnet_id: int
    hostname: Optional[str]
    address: str
    mac: Optional[str]
    type: Optional[DeviceTypeEnum]
    connection_options: list[DeviceConnectionOption]
    connected_with: list[int]

    class Config:
        use_enum_values = True


class PyDeviceFromScanIn(BaseModel):
    ip: str
    mac: str
    ports: list[int]
    is_gateway: bool


class PyFromScanIn(BaseModel):
    agent_token: str
    devices: list[PyDeviceFromScanIn]


class PyFromScanOut(BaseModel):
    created: int
    changed: int
    not_changed: int
    deleted: int
