from fastapi.routing import APIRouter

from echo.routing.agents import router as agents_router
from echo.routing.devices import router as devices_router
from echo.routing.subnets import router as subnets_router
from echo.routing.users import router as users_router


router = APIRouter()


router.include_router(agents_router, prefix='/agents')
router.include_router(devices_router, prefix='/devices')
router.include_router(subnets_router, prefix='/subnets')
router.include_router(users_router, prefix='/account')
