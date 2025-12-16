from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.core.wait_strategies import PortWaitStrategy
from testcontainers.postgres import PostgresContainer

from app.core.config import settings
from app.core.database import get_async_session
from app.core.setup import app


@pytest.fixture
def app_session() -> FastAPI:
    return app


AsyncSessionMaker = async_sessionmaker[AsyncSession]


@pytest_asyncio.fixture(scope="session")
async def postgres_contianer() -> AsyncGenerator[AsyncSessionMaker]:
    """
    Starts a PostgreSQL container, yields the async session maker, and tears it down.
    """
    with PostgresContainer(
        image="postgres:17", username="postgres", password="postgres", dbname="test", driver="postgresql+asyncpg"
    ).waiting_for(PortWaitStrategy(5432)) as postgres:
        postgres_url = postgres.get_connection_url()
        engine: AsyncEngine = create_async_engine(postgres_url)
        session_maker: AsyncSessionMaker = async_sessionmaker(bind=engine, expire_on_commit=False, autocommit=False)
        yield session_maker
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(postgres_contianer) -> AsyncGenerator[AsyncSession]:
    """
    Provides a function-scoped AsyncSession wrapped in a transaction that is rolled back
    after the test finishes to ensure a clean slate for the next test.
    """
    async with postgres_contianer() as session:
        async with session.begin():
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                # Explicitly roll back the transaction to clean up for the next test
                await session.rollback()


@pytest_asyncio.fixture
async def client(app_session: FastAPI, test_session) -> AsyncGenerator[AsyncClient, None]:
    base_url = f"http://{settings.HOST}:${settings.APP_PORT}/api/v1"

    def override_get_async_session():
        yield test_session

    app_session.dependency_overrides[get_async_session] = override_get_async_session
    async with AsyncClient(transport=ASGITransport(app=app_session), base_url=base_url) as client:
        yield client

    # clean up
    app_session.dependency_overrides.pop(get_async_session)
