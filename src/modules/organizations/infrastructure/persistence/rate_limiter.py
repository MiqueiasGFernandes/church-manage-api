import hashlib
from datetime import timedelta

from sqlalchemy import case, delete, func
from sqlalchemy.dialects.postgresql import insert

from modules.organizations.application.errors.auth import RateLimitExceededError
from modules.organizations.application.ports.auth import (
    IRateLimiter,
    RateLimitAction,
    RateLimitPolicies,
)
from modules.organizations.application.ports.registration_services import IClock
from modules.organizations.infrastructure.persistence.database import PostgresDatabase
from modules.organizations.infrastructure.persistence.models import RateLimitModel


class PostgresFixedWindowRateLimiter(IRateLimiter):
    """Share fixed-window counters atomically across application instances."""

    def __init__(
        self, database: PostgresDatabase, clock: IClock, policies: RateLimitPolicies
    ) -> None:
        self._database = database
        self._clock = clock
        self._policies = policies

    async def ensure_allowed(self, action: RateLimitAction, key: str) -> None:
        policy = self._policies[action]
        now = self._clock.now()
        expires_at = now + timedelta(seconds=policy.window_seconds)
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        session = self._database.create_session()

        try:
            await session.execute(delete(RateLimitModel).where(RateLimitModel.expires_at <= now))
            statement = insert(RateLimitModel).values(
                key_hash=key_hash,
                attempts=1,
                window_started_at=now,
                expires_at=expires_at,
            )
            statement = statement.on_conflict_do_update(
                index_elements=[RateLimitModel.key_hash],
                set_={
                    "attempts": case(
                        (RateLimitModel.expires_at <= now, 1),
                        else_=func.least(RateLimitModel.attempts + 1, policy.limit + 1),
                    ),
                    "window_started_at": case(
                        (RateLimitModel.expires_at <= now, now),
                        else_=RateLimitModel.window_started_at,
                    ),
                    "expires_at": case(
                        (RateLimitModel.expires_at <= now, expires_at),
                        else_=RateLimitModel.expires_at,
                    ),
                },
            ).returning(RateLimitModel.attempts)
            attempts = (await session.execute(statement)).scalar_one()
            await session.commit()
        except BaseException:
            await session.rollback()
            raise
        finally:
            await session.close()

        if attempts > policy.limit:
            raise RateLimitExceededError(
                "Limite de tentativas excedido. Tente novamente mais tarde."
            )
