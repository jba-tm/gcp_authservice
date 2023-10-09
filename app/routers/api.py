from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy_utils import database_exists, create_database

from app.contrib.account.api import api as account_api
from app.core.schema import IResponseBase

from .dependency import get_async_db

api = APIRouter()

api.include_router(account_api, tags=["account", "auth"])


@api.get('/database/create/', name='database-create', response_model=IResponseBase[bool])
def create_database(async_db=Depends(get_async_db)):
    """
    Here's why it's not recommended:

    - Performance and Responsiveness: Running database migrations can be a time-consuming process, especially
     if you have a large number of migrations to apply. Running migrations within a FastAPI route could make your
     API endpoint unresponsive or slow for other users during the migration process.

    - Atomicity: Database migrations should be treated as atomic operations. If a migration fails midway,
    you want the database to remain in a consistent state. Running migrations within a FastAPI route makes it more difficult to handle potential errors or rollbacks in a way that ensures the database's integrity.

    - Security: Exposing a route to run database migrations could potentially be a security risk, as it allows
    anyone with access to your API to execute database operations, including potentially harmful ones.

    Instead, it's best to run migrations outside of your application's runtime, typically during deployment
    or as part of your CI/CD (Continuous Integration/Continuous Deployment) pipeline.
    Here's a general process for running migrations:

    - Deployment Script: Create a deployment script or script that runs as part of your deployment process.
    This script should include commands to run Alembic migrations, such as alembic upgrade head.

    - CI/CD Pipeline: If you're using a CI/CD pipeline (e.g., Jenkins, Travis CI, GitHub Actions),
    integrate the deployment script into your pipeline so that migrations are automatically applied during deployment.

    - Manual Execution: In cases where manual intervention is required, run the migration script during
    the deployment process after deploying your FastAPI application.

    By following this approach, you can ensure that migrations are executed safely and consistently without
    affecting the responsiveness of your FastAPI application during runtime.
    :param async_db:
    :return:
    """
    from app.db.models import metadata
    engine = async_db.bind
    database_uri = engine.url.render_as_string(hide_password=False).replace('+asyncpg', '')

    if not database_exists(database_uri):
        create_database(database_uri)

    metadata.create_all(bind=engine)
