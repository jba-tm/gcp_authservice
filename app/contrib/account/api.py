from datetime import timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordRequestForm
from pydantic_core import ErrorDetails, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from fastapi.security.utils import get_authorization_scheme_param

from app.contrib.account.repository import user_repo
from app.core.schema import IResponseBase
from app.utils.jose import JWTError
from app.utils.security import lazy_jwt_settings
from app.routers.dependency import get_async_db, get_current_user, google_id_token_payload
from app.contrib.account.schema import Token, TokenBody, TokenPayload, RefreshTokenBody, UserVisible

from .models import User

api = APIRouter()


def create_token(user_id: int, allow_refresh: bool, aud: str) -> dict:
    payload = lazy_jwt_settings.JWT_PAYLOAD_HANDLER({'user_id': user_id, 'aud': aud})
    jwt_token = lazy_jwt_settings.JWT_ENCODE_HANDLER(payload)
    result = {'access_token': jwt_token, 'token_type': 'bearer', "payload": payload}
    if allow_refresh:
        refresh_payload = lazy_jwt_settings.JWT_PAYLOAD_HANDLER(
            {"user_id": user_id, "jti": uuid4(), "aud": aud},
            expires_delta=timedelta(minutes=lazy_jwt_settings.JWT_REFRESH_EXPIRATION_MINUTES)
        )
        refresh = lazy_jwt_settings.JWT_ENCODE_HANDLER(refresh_payload)
        result["refresh_token"] = refresh
        result["refresh_token_payload"] = refresh_payload
    return result


@api.post('/auth/get-token/', tags=["auth"], name='get-token', response_model=Token)
async def get_token(
        data: OAuth2PasswordRequestForm = Depends(),
        async_db: AsyncSession = Depends(get_async_db),
        id_token_payload: dict = Depends(google_id_token_payload)
) -> dict:
    """
    Get token from external api
    """
    user = await user_repo.authenticate(
        async_db=async_db,
        email=data.username,
        password=data.password,
    )

    if not user:
        raise RequestValidationError(
            [ErrorDetails(
                msg='Incorrect email or password',
                loc=("body", "username",),
                type='value_error',
                input=data.username
            )]
        )

    result = create_token(user.id, allow_refresh=lazy_jwt_settings.JWT_ALLOW_REFRESH, aud=id_token_payload.get('aud'))
    return result


@api.post("/auth/verify-token/", tags=["auth"], name="verify-access-token", response_model=IResponseBase[bool])
async def verify_token(
        token_in: TokenBody
) -> dict:
    if token_in.token.startswith("Bearer"):
        bearer, token = get_authorization_scheme_param(token_in.token)
    else:
        token = token_in.token
    try:
        lazy_jwt_settings.JWT_DECODE_HANDLER(token)
    except (JWTError, ValidationError) as e:
        return {"message": str(e), "data": False}
    return {"message": "Token verified", "data": True}


@api.post(
    "/auth/refresh-token/", tags=["auth"], name="refresh-token", response_model=Token,
    description="Refresh access token"
)
async def new_refresh_token(
        token_in: RefreshTokenBody,
) -> dict:
    """
    Renew new token
    :param token_in:
    :return:
    """
    if not lazy_jwt_settings.JWT_ALLOW_REFRESH:
        raise HTTPException(detail="Refresh token is not allowed", status_code=status.HTTP_400_BAD_REQUEST)
    try:
        payload = lazy_jwt_settings.JWT_DECODE_HANDLER(token_in.refresh_token)
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if token_data.jti is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")

    result = create_token(user_id=token_data.user_id, allow_refresh=token_in.recreate_refresh_token, aud=token_data.aud)
    return result


@api.get("/auth/me/", response_model=UserVisible, name='me')
async def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email
    }
