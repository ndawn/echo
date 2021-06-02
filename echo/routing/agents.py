from secrets import token_urlsafe

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from tortoise.exceptions import IntegrityError

from echo.models.db import Agent, Subnet
from echo.models.pydantic import PyDeleteOut, PyAgent, PyAgentCreateUpdateIn


router = APIRouter()


@router.get('/', response_model=list[PyAgent])
async def list_agents(auth: AuthJWT = Depends()) -> list[PyAgent]:
    auth.jwt_required()

    return [PyAgent.from_orm(agent) for agent in await Agent.all().prefetch_related('subnet')]


@router.get('/:agent_id')
async def get_agent(agent_id: int, auth: AuthJWT = Depends()):
    auth.jwt_required()

    agent = await Agent.get_or_none(pk=agent_id).prefetch_related('subnet')

    if agent is not None:
        return PyAgent.from_orm(agent)
    else:
        raise HTTPException(status_code=404)


@router.post('/', status_code=201, response_model=PyAgent)
async def create_agent(data: PyAgentCreateUpdateIn, auth: AuthJWT = Depends()):
    subnet = await Subnet.get_or_none(pk=data.subnet_id)

    if subnet is None:
        raise HTTPException(status_code=400, detail='Subnet with provided ID does not exist')

    try:
        # TODO: Traceroute to agent ip, add resulting devices, check connectivity with the host, deploy with Ansible

        await Agent.create(address=data.address, subnet=subnet, token=token_urlsafe(48))
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return data


@router.put('/:agent_id', response_model=PyAgent)
async def update_agent(agent_id: int, data: PyAgentCreateUpdateIn, auth: AuthJWT = Depends()):
    auth.jwt_required()

    agent = await Agent.get_or_none(pk=agent_id)

    if agent is None:
        raise HTTPException(status_code=404)

    subnet = await Subnet.get_or_none(pk=data.subnet_id)

    if subnet is None:
        raise HTTPException(status_code=400, detail='Subnet with provided ID does not exist')

    await agent.update_from_dict(data.dict(exclude_none=True, exclude_unset=True))

    try:
        await agent.save()
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return PyAgent.from_orm(agent)


@router.delete('/:agent_id', response_model=PyDeleteOut)
async def delete_agent(agent_id: int, auth: AuthJWT = Depends()):
    auth.jwt_required()

    agent = await Agent.get_or_none(pk=agent_id)

    if agent is None:
        return PyDeleteOut(deleted=False)

    # TODO: Destroy agent at target host

    await agent.delete()

    return PyDeleteOut(deleted=True)
