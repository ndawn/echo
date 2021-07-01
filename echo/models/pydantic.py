from ipaddress import IPv4Address, IPv4Network
from typing import Optional

from pydantic import BaseModel

from echo.models import DeviceTypeEnum, DeviceConnectionOption


class PyDeleteOut(BaseModel):
    deleted: bool


class PySubnet(BaseModel):
    pk: int
    cidr: IPv4Network
    gateway_address: IPv4Address

    class Config:
        orm_mode = True


class PySubnetCreateIn(BaseModel):
    cidr: IPv4Network
    gateway_address: IPv4Address


class PyAgentFull(BaseModel):
    pk: int
    subnet: PySubnet
    address: IPv4Address
    token: str

    class Config:
        orm_mode = True


class PyAgent(BaseModel):
    pk: int
    address: IPv4Address
    subnet: PySubnet

    class Config:
        orm_mode = True


class PyAgentCreateIn(BaseModel):
    address: IPv4Address
    subnet_id: int
    username: str
    password: str


class PyDevice(BaseModel):
    pk: int
    subnet: Optional[PySubnet]
    hostname: Optional[str]
    address: IPv4Address
    mac: Optional[str]
    name: str
    type: DeviceTypeEnum
    connection_options: list[DeviceConnectionOption]
    connected_with: list[int]

    class Config:
        orm_mode = True
        use_enum_values = True


class PyDeviceCreateIn(BaseModel):
    subnet_id: int
    hostname: Optional[str]
    address: IPv4Address
    mac: Optional[str]
    name: str
    type: Optional[DeviceTypeEnum]
    connection_options: list[DeviceConnectionOption]
    connected_with: list[int]

    class Config:
        use_enum_values = True


class PyDeviceUpdateIn(BaseModel):
    name: Optional[str]
    type: Optional[DeviceTypeEnum]

    class Config:
        use_enum_values = True


class PyDeviceTraced(BaseModel):
    ip: IPv4Address
    ports: list[tuple[str, int]]


class PyDeviceFromScanIn(BaseModel):
    ip: IPv4Address
    mac: str
    ports: list[tuple[str, int]]
    is_gateway: bool


class PyFromScanIn(BaseModel):
    agent_token: str
    devices: list[PyDeviceFromScanIn]


class PyFromScanOut(BaseModel):
    created: int
    changed: int
    not_changed: int


class PyUserIn(BaseModel):
    username: str
    password: str


class PyUserOut(BaseModel):
    pk: int
    username: str
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class PyToken(BaseModel):
    access_token: str
