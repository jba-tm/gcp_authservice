from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.conf.config import settings

async_engine = create_async_engine(str(settings.DATABASE_URL), pool_pre_ping=True, echo=False)

db_uri = str(settings.DATABASE_URL).replace('+asyncpg', '')
engine = create_engine(db_uri, pool_pre_ping=True, echo=False)

SessionLocal = sessionmaker(
    expire_on_commit=True,
    autocommit=False,
    autoflush=False,
    # twophase=True,
    bind=engine
)

sync_maker = sessionmaker()
AsyncSessionLocal = async_sessionmaker(
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    # future=True,
    sync_session_class=sync_maker
)

test_db_uri = str(settings.TEST_DATABASE_URL).replace('+asyncpg', '')
testing_engine = create_engine(test_db_uri, pool_pre_ping=True)

test_async_engine = create_async_engine(
    str(settings.TEST_DATABASE_URL), pool_pre_ping=True, echo=False,
)
TestingSessionLocal = sessionmaker(
    expire_on_commit=True,
    # twophase=True,
    autoflush=False,
    autocommit=False,
    bind=testing_engine
)

test_sync_maker = sessionmaker()

AsyncTestingSessionLocal = async_sessionmaker(
    class_=AsyncSession,
    expire_on_commit=False,
    # twophase=True,
    autoflush=False,
    autocommit=False,
    bind=test_async_engine,
    # future=True,
    sync_session_class=test_sync_maker,
# join_transaction_mode="create_savepoint"
)
