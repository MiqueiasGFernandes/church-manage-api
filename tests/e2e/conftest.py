import os
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.main import create_app
from modules.organizations.infrastructure.security import InMemoryEmailSender

TEST_DATABASE_URL = (
    "postgresql+asyncpg://church_manage:church_manage@localhost:5433/church_manage_test"
)
TABLES = (
    "security_audit_events, consumed_refresh_tokens, sessions, password_reset_tokens, "
    "email_verification_tokens, "
    "church_memberships, congregations, "
    "addresses, church_settings, users, churches"
)
database_url = os.environ.get("DATABASE_URL", TEST_DATABASE_URL)
previous_backend = os.environ.get("PERSISTENCE_BACKEND")
previous_database_url = os.environ.get("DATABASE_URL")
try:
    os.environ["PERSISTENCE_BACKEND"] = "postgresql"
    os.environ["DATABASE_URL"] = database_url
    e2e_app = create_app()
finally:
    if previous_backend is None:
        os.environ.pop("PERSISTENCE_BACKEND")
    else:
        os.environ["PERSISTENCE_BACKEND"] = previous_backend
    if previous_database_url is None:
        os.environ.pop("DATABASE_URL")
    else:
        os.environ["DATABASE_URL"] = previous_database_url


@pytest_asyncio.fixture(loop_scope="session")
async def postgres_engine() -> AsyncIterator[AsyncEngine]:
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


@pytest.fixture(scope="session")
def email_sender() -> InMemoryEmailSender:
    sender = e2e_app.state.container.email_sender()
    assert isinstance(sender, InMemoryEmailSender)
    return sender
