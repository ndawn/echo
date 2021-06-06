from secrets import token_urlsafe

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from tortoise.exceptions import IntegrityError

from echo.deploy import deploy, destroy
from echo.models.db import Agent, Subnet
from echo.models.pydantic import PyDeleteOut, PyAgent, PyAgentCreateIn


router = APIRouter()


@router.get('/', response_model=list[PyAgent])
async def list_agents(auth: AuthJWT = Depends()) -> list[PyAgent]:
    auth.jwt_required()

    return [PyAgent.from_orm(agent) for agent in await Agent.all().prefetch_related('subnet')]


@router.get('/{agent_id}')
async def get_agent(agent_id: int, auth: AuthJWT = Depends()):
    auth.jwt_required()

    agent = await Agent.get_or_none(pk=agent_id).prefetch_related('subnet')

    if agent is not None:
        return PyAgent.from_orm(agent)
    else:
        raise HTTPException(status_code=404)


@router.post('/', status_code=201, response_model=PyAgent)
async def create_agent(data: PyAgentCreateIn, auth: AuthJWT = Depends()):
    auth.jwt_required()

    subnet = await Subnet.get_or_none(pk=data.subnet_id)

    if subnet is None:
        raise HTTPException(status_code=400, detail='Subnet with provided ID does not exist')

    try:
        agent = await Agent.create(address=data.address, subnet=subnet, token=token_urlsafe(48))
        await deploy(agent)
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return PyAgent.from_orm(agent)


@router.delete('/{agent_id}', response_model=PyDeleteOut)
async def delete_agent(agent_id: int, auth: AuthJWT = Depends()):
    auth.jwt_required()

    agent = await Agent.get_or_none(pk=agent_id)

    if agent is None:
        return PyDeleteOut(deleted=False)

    destroy(agent)

    await agent.delete()

    return PyDeleteOut(deleted=True)
