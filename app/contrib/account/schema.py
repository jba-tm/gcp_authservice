from typing import Optional
from uuid import UUID
from pydantic import BaseModel as PydanticBaseModel, Field, EmailStr

from app.core.schema import BaseModel, VisibleBase


class UserBase(BaseModel):
    email: EmailStr = Field(alias="email")


class UserCreate(UserBase):
    password: str = Field(..., max_length=50)
    email: EmailStr


class UserVisible(VisibleBase):
    id: int
    email: str


class TokenPayload(PydanticBaseModel):
    user_id: int
    jti: Optional[UUID] = None
    iat: Optional[int] = None
    exp: int
    aud: str


class Token(BaseModel):
    access_token: str
    token_type: str
    payload: "TokenPayload"
    refresh_token: Optional[str] = None
    refresh_token_payload: Optional["TokenPayload"] = None


class TokenBody(BaseModel):
    token: str


class RefreshTokenBody(BaseModel):
    refresh_token: str
    recreate_refresh_token: Optional[bool] = False
