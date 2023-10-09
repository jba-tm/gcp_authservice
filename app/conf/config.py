from typing import List, Optional, Union, Dict, Any
from pathlib import Path
from pydantic import AnyHttpUrl, EmailStr, field_validator, MySQLDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Dirs
    BASE_DIR: Optional[str] = Path(__file__).resolve().parent.parent.parent.as_posix()
    PROJECT_DIR: Optional[str] = Path(__file__).resolve().parent.parent.as_posix()
    # Project
    VERSION: Optional[str] = '0.1.0'
    DEBUG: Optional[bool] = False
    PAGINATION_MAX_SIZE: Optional[int] = 25

    DOMAIN: Optional[str] = 'localhost:8000'
    ENABLE_SSL: Optional[bool] = False
    SITE_URL: Optional[str] = 'http://localhost'
    ROOT_PATH: Optional[str] = ""
    ROOT_PATH_IN_SERVERS: Optional[bool] = True
    OPENAPI_URL: Optional[str] = '/openapi.json'

    API_V1_STR: Optional[str] = "/api/v1"

    SERVER_NAME: Optional[str] = 'localhost'
    SERVER_HOST: Optional[AnyHttpUrl] = 'http://localhost'
    BACKEND_CORS_ORIGINS: Optional[List[str]] = []

    @field_validator("BACKEND_CORS_ORIGINS")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: Optional[str] = 'project_name'

    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASSWORD: str

    model_config = SettingsConfigDict(
        case_sensitive=True, env_file=".env", env_file_encoding='utf-8',
        extra="ignore"
    )


class JWTSettings(BaseSettings):
    # Security
    JWT_SECRET_KEY: Optional[str] = 'change_this'
    # JWT
    JWT_PUBLIC_KEY: Optional[str] = None
    JWT_PRIVATE_KEY: Optional[str] = None
    JWT_ALGORITHM: Optional[str] = "RS256"
    JWT_VERIFY: Optional[bool] = True
    JWT_VERIFY_EXPIRATION: Optional[bool] = True
    JWT_LEEWAY: Optional[int] = 0
    JWT_ARGUMENT_NAME: Optional[str] = 'token'
    JWT_EXPIRATION_MINUTES: Optional[int] = 60 * 24 * 30
    JWT_AUTH_HEADER_NAME: Optional[str] = 'HTTP_AUTHORIZATION'
    JWT_AUTH_HEADER_PREFIX: str = 'Bearer'
    # Helper functions
    JWT_PASSWORD_VERIFY: Optional[str] = 'app.utils.security.verify_password'
    JWT_PASSWORD_HANDLER: Optional[str] = 'app.utils.security.get_password_hash'
    JWT_PAYLOAD_HANDLER: Optional[str] = 'app.utils.security.jwt_payload'
    JWT_ENCODE_HANDLER: Optional[str] = 'app.utils.security.jwt_encode'
    JWT_DECODE_HANDLER: Optional[str] = 'app.utils.security.jwt_decode'
    JWT_AUDIENCE: Optional[str] = 'client'
    JWT_ISSUER: Optional[str] = 'backend'

    model_config = SettingsConfigDict(
        case_sensitive=True, env_file=".env", env_file_encoding='utf-8',
        extra="ignore"
    )


settings = Settings()
jwt_settings = JWTSettings()
