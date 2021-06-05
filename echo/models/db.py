from passlib.context import CryptContext
from tortoise import Model, fields
import ujson

from echo.models import DeviceTypeEnum


crypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class Subnet(Model):
    cidr = fields.CharField(max_length=18, unique=True)
    gateway_address = fields.CharField(max_length=15)


class Agent(Model):
    address = fields.CharField(max_length=15)
    subnet = fields.OneToOneField(model_name='models.Subnet', related_name='agent', on_delete=fields.CASCADE)
    token = fields.CharField(max_length=64)
    username = fields.CharField(max_length=64)
    password = fields.CharField(max_length=64)


class Device(Model):
    subnet = fields.ForeignKeyField(
        model_name='models.Subnet',
        related_name='devices',
        on_delete=fields.RESTRICT,
    )
    hostname = fields.CharField(max_length=255, default='')
    address = fields.CharField(max_length=15, unique=True)
    mac = fields.CharField(max_length=17, unique=True, null=True)
    name = fields.CharField(max_length=64, default='')
    type = fields.CharEnumField(enum_type=DeviceTypeEnum)
    connection_options = fields.JSONField(encoder=ujson.dumps, decoder=ujson.loads)
    connected_with = fields.JSONField(encoder=ujson.dumps, decoder=ujson.loads)


class User(Model):
    username = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=255)
    first_name = fields.CharField(max_length=32)
    last_name = fields.CharField(max_length=64)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return crypt_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(plain_password: str) -> str:
        return crypt_context.hash(plain_password)
