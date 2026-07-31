from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def psycopg_url(database_url: str) -> URL:
    """Select Psycopg at the infrastructure boundary without changing DATABASE_URL."""
    return make_url(database_url).set(drivername="postgresql+psycopg")


class PostgresDatabase:
    """Own the PostgreSQL engine and create one session per application operation."""

    def __init__(self, database_url: str) -> None:
        if not database_url:
            raise ValueError("DATABASE_URL é obrigatória para a persistência PostgreSQL.")
        self._engine: AsyncEngine = create_async_engine(
            psycopg_url(database_url), pool_pre_ping=True
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    def create_session(self) -> AsyncSession:
        return self._session_factory()

    async def dispose(self) -> None:
        await self._engine.dispose()
