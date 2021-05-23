from fastapi.routing import APIRouter


router = APIRouter()


@router.get('/')
async def get():
    pass
