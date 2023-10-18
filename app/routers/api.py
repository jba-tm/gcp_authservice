from fastapi import APIRouter

from app.contrib.account.api import api as account_api
from app.core.schema import IResponseBase
from app.conf.config import jwt_settings

api = APIRouter()

api.include_router(account_api, tags=["account", "auth"])


@api.get("/public-key/", name='public-key', response_model=IResponseBase[str])
async def get_public_key():
    return {
        "data": jwt_settings.JWT_PUBLIC_KEY
    }
