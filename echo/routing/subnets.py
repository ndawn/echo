from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from tortoise.exceptions import IntegrityError

from echo.models.db import Subnet
from echo.models.pydantic import PyDeleteOut, PySubnet


router = APIRouter()


@router.get('/', response_model=list[PySubnet])
async def list_subnets(auth: AuthJWT = Depends()) -> list[PySubnet]:
    auth.jwt_required()

    return [PySubnet.from_orm(subnet) for subnet in await Subnet.all()]


@router.get('/{subnet_id}')
async def get_subnet(subnet_id: int, auth: AuthJWT = Depends()):
    auth.jwt_required()

    subnet = await Subnet.get_or_none(pk=subnet_id)

    if subnet is not None:
        return PySubnet.from_orm(subnet)
    else:
        raise HTTPException(status_code=404)


@router.post('/', status_code=201, response_model=PySubnet)
async def create_subnet(data: PySubnet, auth: AuthJWT = Depends()):
    auth.jwt_required()

    try:
        await Subnet.create(**data.dict())
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return data


@router.delete('/{subnet_id}', response_model=PyDeleteOut)
async def delete_subnet(subnet_id: int, auth: AuthJWT = Depends()):
    auth.jwt_required()

    subnet = await Subnet.get_or_none(pk=subnet_id)

    if subnet is None:
        return PyDeleteOut(deleted=False)

    await subnet.devices.all().delete()  # noqa
    await subnet.agent.delete()  # noqa
    await subnet.delete()

    return PyDeleteOut(deleted=True)
