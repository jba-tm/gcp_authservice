from typing import Generator

from fastapi import Depends

from google.auth.exceptions import GoogleAuthError
from google.oauth2 import id_token
from google.auth.transport.requests import Request as GoogleRequest

from app.utils.security import OAuth2PasswordBearerWithCookie
from app.conf.config import settings
from app.contrib.account.schema import TokenPayload
from app.core.exceptions import HTTPInvalidToken
from app.db.session import get_async_session

reusable_oauth2 = OAuth2PasswordBearerWithCookie(tokenUrl=f'{settings.API_V1_STR}/auth/get-token/', auto_error=False)


async def get_token_payload(
        token: str = Depends(reusable_oauth2),
) -> TokenPayload:
    try:
        id_info = id_token.verify_oauth2_token(token, GoogleRequest())
        return id_info
    except GoogleAuthError as e:
        raise HTTPInvalidToken(detail=str(e))


async def get_async_db(token_payload: TokenPayload) -> Generator:
    async_session_local = get_async_session(token_payload.aud)
    try:
        async with async_session_local() as session:
            yield session
    except Exception as e:
        raise HTTPInvalidToken(detail=str(e), status_code=500)
    finally:
        await session.close()
