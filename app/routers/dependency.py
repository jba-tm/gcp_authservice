import json
from typing import Generator, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request
from pydantic import ValidationError
from starlette.status import HTTP_403_FORBIDDEN
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.security import lazy_jwt_settings, OAuth2PasswordBearerWithCookie
from app.conf.config import settings
from app.contrib.account.schema import TokenPayload, User

from app.contrib.account.repository import user_repo, user_session_repo
from app.core.exceptions import HTTPUnAuthorized, HTTPInvalidToken, HTTPPermissionDenied
from app.core.schema import CommonsModel
from app.utils.jose import jwt
from app.db.session import AsyncSessionLocal, SessionLocal

reusable_oauth2 = OAuth2PasswordBearerWithCookie(tokenUrl=f'{settings.API_V1_STR}/auth/get-token/', auto_error=False)




async def get_async_db() -> Generator:
    try:
        async with AsyncSessionLocal() as session:
            yield session
    finally:
        await session.close()


async def get_token_payload(
        token: str = Depends(reusable_oauth2),
) -> TokenPayload:
    try:
        payload = lazy_jwt_settings.JWT_DECODE_HANDLER(token)
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPUnAuthorized
    return token_data


async def get_current_user(
        token_payload: TokenPayload = Depends(get_token_payload),
        async_db: AsyncSession = Depends(get_async_db),
        aioredis_instance: AIRedis = Depends(get_aioredis),
) -> dict:
    """
    Get user by token
    :param token_payload:
    :param async_db:
    :param aioredis_instance:
    :return:
    """
    user_cache = await aioredis_instance.get(f'session:{token_payload.jti}')
    if not user_cache:
        user_session = await user_session_repo.first(
            async_db=async_db,
            params={'id': UUID(token_payload.jti), "revoked_at": None}
        )
        if not user_session:
            raise HTTPPermissionDenied

        user = await user_repo.first(async_db=async_db, params={'id': token_payload.user_id})
        if not user:
            raise HTTPInvalidToken(detail="Invalid token")
        data = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "compony": user.company,
            "email_verified_at": user.email_verified_at,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at,
        }
        data_dumps = json.dumps(data)
        await aioredis_instance.set(name=f"session:{token_payload.jti}", value=data_dumps, ex=3600)
    else:
        data = json.loads(user_cache)
    return data


async def get_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Your account is disabled")
    elif user.email_verified_at is None:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Your email is not verified")
    return user


async def get_commons(
        page: Optional[int] = 1,
        limit: Optional[int] = settings.PAGINATION_MAX_SIZE,
) -> CommonsModel:
    """

    Get commons dict for list pagination
    :param limit:
    :param page:
    :return:
    """
    if not page or not isinstance(page, int):
        page = 1
    elif page < 0:
        page = 1
    offset = (page - 1) * limit
    return CommonsModel(
        limit=limit,
        offset=offset,
        page=page,
    )
