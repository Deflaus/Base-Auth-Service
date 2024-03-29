from fastapi import APIRouter

from api.v1 import auth as auth_v1
from api.v1 import users as users_v1

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(auth_v1.router, prefix="/auth", tags=["auth"])
v1_router.include_router(users_v1.router, prefix="/users", tags=["users"])

api_router = APIRouter(prefix="/api")
api_router.include_router(v1_router)
