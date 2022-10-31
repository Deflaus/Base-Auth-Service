from fastapi import APIRouter

from schemas.auth import TokenPairSchema

router = APIRouter()


@router.post("/sign_in/", response_model=TokenPairSchema)
async def sign_in() -> TokenPairSchema:
    return TokenPairSchema(access="", refresh="")
