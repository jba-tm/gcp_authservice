from typing import Optional

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


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(PydanticBaseModel):
    aud: str


class VerifyToken(PydanticBaseModel):
    access_token: Optional[str] = Field(None)
