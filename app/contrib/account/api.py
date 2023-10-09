from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordRequestForm
from pydantic_core import ErrorDetails
from sqlalchemy.ext.asyncio import AsyncSession

from app.contrib.account.repository import user_repo
from app.utils.security import lazy_jwt_settings
from app.routers.dependency import get_async_db
from app.contrib.account.schema import Token

api = APIRouter()


@api.post('/auth/get-token/', name='get-token', response_model=Token)
async def get_token(
        data: OAuth2PasswordRequestForm = Depends(),
        async_db: AsyncSession = Depends(get_async_db),
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

    payload = lazy_jwt_settings.JWT_PAYLOAD_HANDLER(
        {
            'user_id': user.id,
            'aud': lazy_jwt_settings.JWT_AUDIENCE,
        },
    )
    jwt_token = lazy_jwt_settings.JWT_ENCODE_HANDLER(payload)
    result = {'access_token': jwt_token, 'token_type': 'bearer'}

    return result


# @api.get('/auth/verify-token/', name='verify-token', response_model=IResponseBase[bool])
# async def verify_token(
#         request: Request,
# ):
#     return {
#         "message": "Token verified",
#         "data": True
#     }


# @api.get("/auth/me/", response_model=UserVisible, name='me')
# async def get_me(
#         user: User = Depends(get_current_user)
# ):
#     return user
