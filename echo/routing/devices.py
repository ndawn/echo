from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from tortoise.exceptions import IntegrityError

from echo.models import DeviceTypeEnum
from echo.models.db import Agent, Device, Subnet
from echo.models.pydantic import PyDeleteOut, PyDevice, PyDeviceCreateUpdateIn, PyFromScanIn, PyFromScanOut


router = APIRouter()


@router.get('/', response_model=list[PyDevice])
async def list_devices(auth: AuthJWT = Depends()) -> list[PyDevice]:
    auth.jwt_required()

    return [PyDevice.from_orm(device) for device in await Device.all().prefetch_related('subnet')]


@router.get('/{device_id}')
async def get_device(device_id: int, auth: AuthJWT = Depends()):
    auth.jwt_required()

    device = await Device.get_or_none(pk=device_id).prefetch_related('subnet')

    if device is None:
        raise HTTPException(status_code=404)

    return PyDevice.from_orm(device)


@router.post('/', status_code=201, response_model=PyDevice)
async def create_device(data: PyDeviceCreateUpdateIn, auth: AuthJWT = Depends()):
    auth.jwt_required()

    subnet = await Subnet.get_or_none(pk=data.subnet_id)

    if subnet is None:
        raise HTTPException(status_code=400, detail='Subnet with provided ID does not exist')

    try:
        device = await Device.create(**data.dict(exclude_none=True, exclude_unset=True))
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return PyDevice.from_orm(device)


@router.put('/{device_id}', response_model=PyDevice)
async def update_device(device_id: int, data: PyDeviceCreateUpdateIn, auth: AuthJWT = Depends()):
    auth.jwt_required()

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


@router.delete('/{device_id}', response_model=PyDeleteOut)
async def delete_device(device_id: int, auth: AuthJWT = Depends()):
    auth.jwt_required()

    device = await Device.get_or_none(pk=device_id)

    if device is None:
        return PyDeleteOut(deleted=False)

    await device.delete()

    return PyDeleteOut(deleted=True)


@router.post(
    '/from_scan',
    response_model=PyFromScanOut,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
)
async def from_scan(data: PyFromScanIn) -> PyFromScanOut:
    agent = await Agent.get_or_none(token=data.agent_token).prefetch_related('subnet')

    if agent is None:
        raise HTTPException(status_code=401, detail='Token is invalid or missing')

    try:
        gateway_data = next(filter(lambda x: x.is_gateway, data.devices))
    except StopIteration:
        raise HTTPException(status_code=400, detail='Gateway data is missing in scan data')

    gateway = await Device.get_or_none(address=agent.subnet.gateway_address)

    if gateway is None:
        gateway = await Device.create(
            subnet=agent.subnet,
            address=gateway_data.ip,
            mac=gateway_data.mac,
            type=DeviceTypeEnum.UNKNOWN,
            connection_options=gateway_data.ports,
            connected_with=[],
        )

    all_subnet_devices = [
        x[0] for x in await Device.filter(subnet_id=agent.subnet_id).exclude(address=gateway.address).values_list('id')
    ]

    created = changed = not_changed = deleted = 0
    is_changed = False

    agent.subnet.gateway_address = gateway_data.ip
    await agent.subnet.save()

    if gateway.address != gateway_data.ip:
        is_changed = True
        gateway.address = gateway_data.ip

    if gateway.mac != gateway_data.mac:
        is_changed = True
        gateway.mac = gateway_data.mac

    if tuple(gateway.connection_options) != tuple(gateway_data.ports):
        is_changed = True
        gateway.connection_options = gateway_data.ports

    if is_changed:
        changed += 1
        await gateway.save()
    else:
        not_changed += 1

    for device_data in data.devices:
        if device_data.is_gateway:
            continue

        is_changed = is_created = False

        device = await Device.get_or_none(subnet=agent.subnet, address=device_data.ip)

        if device is None:
            device = Device(
                subnet=agent.subnet,
                address=device_data.ip,
                mac=device_data.mac,
                type=DeviceTypeEnum.UNKNOWN,
                connection_options=device_data.ports,
                connected_with=[gateway.pk],
            )

            is_created = True
        else:
            if device.mac != device_data.mac:
                is_changed = True
                device.mac = device_data.mac

            if tuple(device.connection_options) != tuple(device_data.ports):
                is_changed = True
                device.connection_options = device_data.ports

        if is_changed or is_created:
            await device.save()

            if device.pk in all_subnet_devices:
                all_subnet_devices.remove(device.pk)

        if is_created:
            created += 1
        elif is_changed:
            changed += 1
        else:
            not_changed += 1

    for subnet_device_id in all_subnet_devices:
        subnet_device = await Device.get_or_none(pk=subnet_device_id)

        if subnet_device is not None:
            deleted += 1
            await subnet_device.delete()

    return PyFromScanOut(
        created=created,
        changed=changed,
        not_changed=not_changed,
        deleted=deleted,
    )
