from tortoise import Model, fields
import ujson

from echo.models import DeviceTypeEnum


class Device(Model):
    hostname = fields.CharField(max_length=255, default='unknown')
    address = fields.CharField(max_length=15)
    mac = fields.CharField(max_length=17, null=True)
    type = fields.CharEnumField(DeviceTypeEnum)
    os = fields.CharField(max_length=32, default='unknown')
    connection_options = fields.JSONField(encoder=ujson.dumps, decoder=ujson.loads)
    connected_with = fields.JSONField(encoder=ujson.dumps, decoder=ujson.loads)
    raw_scan_data = fields.JSONField(encoder=ujson.dumps, decoder=ujson.loads)


class Agent(Model):
    address = fields.CharField(max_length=15)
    key = fields.CharField(max_length=64)
