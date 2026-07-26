import os
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.main import create_app

TABLES = "church_memberships, congregations, addresses, church_settings, users, churches"
e2e_app = create_app()


@pytest_asyncio.fixture(loop_scope="session")
async def postgres_engine() -> AsyncIterator[AsyncEngine]:
    if os.getenv("PERSISTENCE_BACKEND") != "postgresql":
        pytest.skip("Os testes E2E de cadastro exigem PERSISTENCE_BACKEND=postgresql.")

    database_url = os.environ.get("DATABASE_URL", "")
    if "church_manage_test" not in database_url:
        pytest.fail("DATABASE_URL deve apontar explicitamente para church_manage_test.")

    engine = create_async_engine(database_url)

    async def truncate_registration_tables() -> None:
        async with engine.begin() as connection:
            await connection.execute(text(f"TRUNCATE TABLE {TABLES} CASCADE"))

    await truncate_registration_tables()
    yield engine
    await truncate_registration_tables()
    await engine.dispose()


@pytest_asyncio.fixture(loop_scope="session")
async def api_client(postgres_engine: AsyncEngine) -> AsyncIterator[AsyncClient]:
    assert postgres_engine is not None
    async with AsyncClient(
        transport=ASGITransport(app=e2e_app),
        base_url="http://test",
    ) as client:
        yield client
