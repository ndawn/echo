from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

from echo.config import JWT_SECRET_KEY
from echo.models.db import User
from echo.models.pydantic import PyToken, PyUserIn, PyUserOut


router = APIRouter()


class JWTConfig(BaseModel):
    authjwt_secret_key: str = JWT_SECRET_KEY


@AuthJWT.load_config
def get_config():
    return JWTConfig()


@router.get('/', response_model=PyUserOut)
async def get_user(auth: AuthJWT = Depends()):
    auth.jwt_required()

    user_id = auth.get_jwt_subject()
    user = await User.get_or_none(pk=user_id)

    if user is None:
        raise HTTPException(status_code=404)

    return PyUserOut.from_orm(user)


@router.post('/login', response_model=PyToken)
async def login(data: PyUserIn, auth: AuthJWT = Depends()):
    user = await User.get_or_none(username=data.username)

    if user is None:
        raise HTTPException(status_code=401, detail='Invalid username or password')

    if not User.verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail='Invalid username or password')

    access_token = auth.create_access_token(user.pk, expires_time=3600)

    return PyToken(access_token=access_token)
