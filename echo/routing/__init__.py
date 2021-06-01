from fastapi import HTTPException
from fastapi.routing import APIRouter

from echo.models import DeviceTypeEnum
from echo.models.db import Agent, Device
from echo.models.pydantic import PyFromScanIn, PyFromScanOut
from echo.routing.agents import router as agents_router
from echo.routing.devices import router as devices_router
from echo.routing.subnets import router as subnets_router


router = APIRouter()


router.include_router(agents_router, prefix='/agents')
router.include_router(devices_router, prefix='/devices')
router.include_router(subnets_router, prefix='/subnets')


@router.post(
    '/devices/from_scan',
    status_code=200,
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

    all_subnet_devices = list(
        await Device.filter(subnet_id=agent.subnet_id).exclude(address=gateway.address).values_list('pk')
    )

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
