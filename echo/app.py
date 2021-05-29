from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from echo import config
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
