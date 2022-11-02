from fastapi import APIRouter

from api.v1 import auth

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])
