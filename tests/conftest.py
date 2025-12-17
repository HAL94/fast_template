from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database.url import DATABASE_URL

AsyncSessionMaker = async_sessionmaker[AsyncSession]


@pytest_asyncio.fixture
async def async_session() -> AsyncGenerator[AsyncSession]:
    """
    Provides a function-scoped AsyncSession wrapped in a transaction that is rolled back
    after the test finishes to ensure a clean slate for the next test.
    """
    engine: AsyncEngine = create_async_engine(DATABASE_URL, future=True)

    session_maker = AsyncSessionMaker(
        autocommit=False,
        bind=engine,
        expire_on_commit=False,
    )

    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await engine.dispose()


@pytest.fixture
def fast_api(async_session: AsyncSession) -> Generator[FastAPI, None]:
    from app.core.database import get_async_session  # noqa: PLC0415
    from app.core.setup import app  # noqa: PLC0415

    async def _get_test_db():
        yield async_session

    app.dependency_overrides[get_async_session] = _get_test_db
    yield app
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(fast_api: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Base client for the use of testing routes"""
    base_url = f"http://{settings.HOST}:{settings.APP_PORT}/api/v1"
    async with AsyncClient(transport=ASGITransport(app=fast_api), base_url=base_url) as client:
        yield client
