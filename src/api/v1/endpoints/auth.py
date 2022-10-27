from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter()


@router.post("/sign_in/")
async def sign_in():
    return Response(status_code=201)
