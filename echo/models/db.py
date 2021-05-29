from tortoise import Model, fields
import ujson

from echo.models import DeviceTypeEnum


class Subnet(Model):
    cidr = fields.CharField(max_length=18, unique=True)
    gateway_address = fields.CharField(max_length=15)


class Agent(Model):
    address = fields.CharField(max_length=15)
    subnet = fields.OneToOneField(model_name='models.Subnet', related_name='agent', on_delete=fields.CASCADE)
    token = fields.CharField(max_length=64)


class Device(Model):
    subnet = fields.ForeignKeyField(
        model_name='models.Subnet',
        related_name='devices',
        on_delete=fields.RESTRICT,
    )
    hostname = fields.CharField(max_length=255, default='')
    address = fields.CharField(max_length=15, unique=True)
    mac = fields.CharField(max_length=17, unique=True, null=True)
    type = fields.CharEnumField(enum_type=DeviceTypeEnum)
    connection_options = fields.JSONField(encoder=ujson.dumps, decoder=ujson.loads)
    connected_with = fields.JSONField(encoder=ujson.dumps, decoder=ujson.loads)
