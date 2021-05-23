from enum import Enum


class SerializableEnum(Enum):
    def serialize(self):
        return self.value


class DeviceConnectionTypeEnum(SerializableEnum):
    SSH = 'ssh'
    TELNET = 'telnet'
    RDP = 'rdp'
    VNC = 'vnc'


DeviceConnectionOption = tuple[str, int]


class DeviceTypeEnum(SerializableEnum):
    UNKNOWN = 'unknown'
    PC = 'pc'
    MOBILE = 'mobile'
    SERVER = 'server'
    ECHO = 'echo'
    SWITCH = 'switch'
    ROUTER = 'router'
    ACCESS_POINT = 'access_point'
    VOIP = 'voip'
    PRINTER = 'printer'


class DeviceStatusEnum(SerializableEnum):
    DOWN = 'down'
    UP = 'up'
