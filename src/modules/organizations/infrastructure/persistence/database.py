from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class PostgresDatabase:
    """Own the PostgreSQL engine and create one session per application operation."""

    def __init__(self, database_url: str) -> None:
        if not database_url:
            raise ValueError("DATABASE_URL é obrigatória para a persistência PostgreSQL.")
        self._engine: AsyncEngine = create_async_engine(database_url, pool_pre_ping=True)
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    def create_session(self) -> AsyncSession:
        return self._session_factory()

    async def dispose(self) -> None:
        await self._engine.dispose()
