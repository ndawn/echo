from tortoise import Model, Tortoise, fields
import ujson

from models import DeviceTypeEnum

import config


async def init_db_models():
    await Tortoise.init(
        db_url=config.DATABASE_URL,
        modules={'models': ['models.db']},
    )

    await Tortoise.generate_schemas()


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
