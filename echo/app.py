from fastapi import FastAPI
from tortoise import run_async

from echo.models.db import init_db_models
from echo.router import router


run_async(init_db_models())

app = FastAPI()
app.include_router(router)
