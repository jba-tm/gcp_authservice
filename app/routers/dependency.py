from typing import Generator

from fastapi import Depends, Request, HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import ValidationError
from starlette.status import HTTP_401_UNAUTHORIZED

from sqlalchemy.ext.asyncio import AsyncSession

from google.auth.exceptions import GoogleAuthError
from google.oauth2 import id_token
from google.auth.transport.requests import Request as GoogleRequest

from app.contrib.account.repository import user_repo
from app.utils.jose import JWTError
from app.utils.security import OAuth2PasswordBearerWithCookie
from app.conf.config import settings
from app.contrib.account.schema import TokenPayload
from app.core.exceptions import HTTPInvalidToken, HTTPPermissionDenied
from app.db.session import get_async_session
from app.utils.security import lazy_jwt_settings
from app.contrib.account.models import User

reusable_oauth2 = OAuth2PasswordBearerWithCookie(tokenUrl=f'{settings.API_V1_STR}/auth/get-token/', auto_error=False)


async def get_google_id_token(request: Request):
    header_authorization: str = request.headers.get(lazy_jwt_settings.JWT_GIT_HEADER_NAME)
    cookie_authorization: str = request.cookies.get(lazy_jwt_settings.JWT_GIT_COOKIE_NAME)
    header_scheme, header_param = get_authorization_scheme_param(header_authorization)
    cookie_scheme, cookie_param = get_authorization_scheme_param(cookie_authorization)
    if header_scheme.lower() == "bearer":
        authorization = True
        scheme = header_scheme
        param = header_param
    elif cookie_scheme.lower() == "bearer":
        authorization = True
        scheme = cookie_scheme
        param = cookie_param
    else:
        authorization = False
        scheme = ''
        param = None

    if not authorization or scheme.lower() != "bearer":
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return param


async def google_id_token_payload(token: str = Depends(get_google_id_token)):
    try:
        id_info = id_token.verify_oauth2_token(token, GoogleRequest())
    except GoogleAuthError as e:
        raise HTTPInvalidToken(detail=str(e))
    return id_info


async def get_token_payload(
        token: str = Depends(reusable_oauth2),
) -> TokenPayload:
    try:
        payload = lazy_jwt_settings.JWT_DECODE_HANDLER(token)
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError) as e:
        raise HTTPInvalidToken(detail=str(e))
    return token_data


async def get_async_db(id_token_payload: dict = Depends(google_id_token_payload)) -> Generator:
    async_session_local, _ = get_async_session(id_token_payload.get("aud"))
    try:
        async with async_session_local() as session:
            yield session
    except Exception as e:
        raise HTTPInvalidToken(detail=str(e), status_code=500)
    finally:
        await session.close()


async def get_current_user(
        token_payload: TokenPayload = Depends(get_token_payload),
        async_db: AsyncSession = Depends(get_async_db),
) -> dict:
    """
    Get user by token
    :param token_payload:
    :param async_db:
    :return:
    """
    user = await user_repo.first(async_db=async_db, params={'id': token_payload.user_id})
    if not user:
        raise HTTPInvalidToken(detail="Invalid token")

    return user
