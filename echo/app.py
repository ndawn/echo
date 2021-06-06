from socket import gethostname, gethostbyname

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import UJSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException
from tortoise.contrib.fastapi import register_tortoise
import ujson

from echo import config
from echo.models.db import Device, DeviceTypeEnum
from echo.routing import router


app = FastAPI()
app.include_router(router)

register_tortoise(
    app,
    db_url=config.DATABASE_URL,
    modules={'models': ['echo.models.db']},
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exception: AuthJWTException):
    return UJSONResponse(status_code=exception.status_code, content={'detail': exception.message})  # noqa
