from datetime import timedelta
from pprint import pprint
from starlette import status
from calendar import timegm

from typing import TYPE_CHECKING

from app.conf.config import settings, jwt_settings

from app.utils.datetime.timezone import now
from app.utils.security import lazy_jwt_settings

if TYPE_CHECKING:
    from app.contrib.account.models import User
    from fastapi.testclient import TestClient


def test_admin_get_token_api(
        admin_client: "TestClient",
        staff_user: "User",
        simple_user: "User",
) -> None:
    response = admin_client.post(
        f'{settings.API_V1_STR}/auth/get-token/',
        data={
            'username': staff_user.email,
            'password': "test_secret",
        }
    )
    assert response.status_code == status.HTTP_200_OK

    response = admin_client.post(
        f'{settings.API_V1_STR}/auth/get-token/',
        data={
            'username': "invalid@example.com",
            'password': "test_secret",
        }
    )
    result = response.json()
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert result == {'detail': [{'input': 'invalid@example.com',
                                  'loc': ['email'],
                                  'msg': 'Incorrect email or password',
                                  'type': 'value_error'}]}

    response = admin_client.post(
        f'{settings.API_V1_STR}/auth/get-token/',
        data={
            'username': simple_user.email,
            'password': "test_secret",
        }
    )
    result = response.json()
    assert result == {
        'detail': [{'input': 'user@example.com',
                    'loc': ['email'],
                    'msg': 'Staff member required to access admin functions',
                    'type': 'value_error'}]
    }

