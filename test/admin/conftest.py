import pytest
from typing import Any, Generator, Callable, Optional, List, TYPE_CHECKING
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import get_application
from app.conf.config import settings
from app.routers import dependency
from app.routers.urls import router
from app.contrib.admin.api import api as admin_api

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


@pytest.fixture
def admin_user(get_user):
    return get_user(
        email=settings.FIRST_SUPERUSER,
        is_superuser=True,
    )


@pytest.fixture(autouse=True)
def admin_application(
        test_db
) -> Generator[FastAPI, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db` fixture to override
    the `get_db` dependency that is injected into routes.
    """

    def _get_test_db():
        yield test_db

    _app = get_application(
        root_path=settings.ADMIN_ROOT_PATH,
        root_path_in_servers=settings.ADMIN_ROOT_PATH_IN_SERVERS,
        openapi_url=settings.OPENAPI_URL,
        app_router=router,
        app_api=admin_api,
        api_prefix=settings.API_V1_STR,
    )

    _app.dependency_overrides[dependency.get_db] = _get_test_db
    yield _app


@pytest.fixture
def admin_client(admin_application: FastAPI, test_db: "Session") -> Generator[TestClient, Any, None]:
    with TestClient(admin_application) as client:
        yield client
