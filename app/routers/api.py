from fastapi import APIRouter

from app.contrib.account.api import api as account_api
from app.core.schema import IResponseBase

api = APIRouter()

api.include_router(account_api, tags=["account", "auth"])


@api.get('/database/create/', name='database-create', response_model=IResponseBase[bool])
async def create_database():
    return {
        "message": "Database created",
        "data": True
    }
