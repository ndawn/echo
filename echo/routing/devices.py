from secrets import token_urlsafe

from fastapi import HTTPException
from fastapi.routing import APIRouter
from tortoise.exceptions import IntegrityError

from echo.models.db import Device, Subnet
from echo.models.pydantic import PyDeleteOut, PyDevice, PyDeviceCreateUpdateIn


router = APIRouter()


@router.get('/', response_model=list[PyDevice])
async def list_devices() -> list[PyDevice]:
    return [PyDevice.from_orm(device) for device in await Device.all().prefetch_related()]


@router.get('/:device_id')
async def get_device(device_id: int):
    device = await Device.get_or_none(pk=device_id).prefetch_related()

    if device is None:
        raise HTTPException(status_code=404)

    return PyDevice.from_orm(device)


@router.post('/', status_code=201, response_model=PyDevice)
async def create_device(data: PyDeviceCreateUpdateIn):
    subnet = await Subnet.get_or_none(pk=data.subnet_id)

    if subnet is None:
        raise HTTPException(status_code=400, detail='Subnet with provided ID does not exist')

    try:
        device = await Device.create(**data.dict(exclude_none=True, exclude_unset=True))
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return PyDevice.from_orm(device)


@router.put('/:device_id', response_model=PyDevice)
async def update_device(device_id: int, data: PyDeviceCreateUpdateIn):
    device = await Device.get_or_none(pk=device_id)

    if device is None:
        raise HTTPException(status_code=404)

    subnet = await Subnet.get_or_none(pk=data.subnet_id)

    if subnet is None:
        raise HTTPException(status_code=400, detail='Subnet with provided ID does not exist')

    await device.update_from_dict(data.dict(exclude_none=True, exclude_unset=True))

    try:
        await device.save()
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return PyDevice.from_orm(device)


@router.delete('/:device_id', response_model=PyDeleteOut)
async def delete_device(device_id: int):
    device = await Device.get_or_none(pk=device_id)

    if device is None:
        return PyDeleteOut(deleted=False)

    await device.delete()

    return PyDeleteOut(deleted=True)
