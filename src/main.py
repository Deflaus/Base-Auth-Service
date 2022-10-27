from fastapi import FastAPI

from api import api_router


app = FastAPI(title="Base Auth Service")
app.include_router(api_router)
