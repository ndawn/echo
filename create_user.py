import argparse
import asyncio

from tortoise import Tortoise

from echo.config import DATABASE_URL
from echo.models.db import User


parser = argparse.ArgumentParser()

parser.add_argument('--username', type=str)
parser.add_argument('--password', type=str)
parser.add_argument('--first-name', type=str)
parser.add_argument('--last-name', type=str)


async def main(args):
    await Tortoise.init(db_url=DATABASE_URL, modules={'models': ['echo.models.db']})
    await Tortoise.generate_schemas()

    await User.create(
        username=args.username,
        password=User.get_password_hash(args.password),
        first_name=args.first_name,
        last_name=args.last_name,
    )

    await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(main(parser.parse_args()))
