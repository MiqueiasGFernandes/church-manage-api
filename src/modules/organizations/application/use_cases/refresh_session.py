import logging
from datetime import timedelta
from uuid import UUID

from modules.organizations.application.dto.auth import (
    TokenPair,
)
from modules.organizations.application.errors.auth import (
    InvalidRefreshTokenError,
    SessionRevokedError,
)
from modules.organizations.application.ports.auth import (
    ITokenService,
)
from modules.organizations.application.ports.registration_services import (
    IClock,
    IUnitOfWork,
)
from modules.organizations.application.repositories.auth_repository import (
    IAuthRepository,
    SecurityAuditEvent,
)
from modules.organizations.domain.model import UserStatus
from modules.organizations.domain.use_cases.refresh_session import IRefreshSession

logger = logging.getLogger(f"church_manage.{__name__}")


class RefreshSession(IRefreshSession):
    def __init__(
        self,
        repository: IAuthRepository,
        unit_of_work: IUnitOfWork,
        tokens: ITokenService,
        clock: IClock,
    ) -> None:
        self._repository, self._unit_of_work, self._tokens, self._clock = (
            repository,
            unit_of_work,
            tokens,
            clock,
        )

    async def execute(self, refresh_token: str) -> TokenPair:
        now = self._clock.now()
        token_hash = self._tokens.hash_opaque(refresh_token)
        reused = False
        result: TokenPair | None = None
        authenticated_user_id: UUID | None = None
        async with self._unit_of_work:
            session = await self._repository.find_session_by_refresh(token_hash)
            if session is None:
                reused_session_id = await self._repository.find_session_id_by_consumed_refresh(
                    token_hash
                )
                if reused_session_id is None:
                    raise InvalidRefreshTokenError("Refresh token inválido.")
                await self._repository.revoke_session(reused_session_id, now)
                await self._repository.add_audit_event(
                    SecurityAuditEvent(
                        "SUSPICIOUS_REFRESH_TOKEN_REUSE",
                        now,
                        session_id=reused_session_id,
                    )
                )
                await self._unit_of_work.commit()
                reused = True
            elif session.expires_at <= now:
                raise InvalidRefreshTokenError("Refresh token inválido.")
            elif session.revoked_at is not None:
                raise SessionRevokedError("A sessão foi revogada.")
            else:
                user = await self._repository.find_user_by_id(session.user_id)
                if user is None or user.status is not UserStatus.ACTIVE:
                    raise InvalidRefreshTokenError("Refresh token inválido.")
                refresh = self._tokens.generate_opaque()
                await self._repository.add_consumed_refresh_token(session.id, token_hash, now)
                await self._repository.rotate_session(
                    session.id, self._tokens.hash_opaque(refresh), now + timedelta(days=14)
                )
                await self._repository.add_audit_event(
                    SecurityAuditEvent(
                        "SESSION_REFRESHED", now, actor_user_id=user.id.value, session_id=session.id
                    )
                )
                access, expires_in = self._tokens.issue_access(user.id.value, session.id, now)
                result = TokenPair(access, refresh, expires_in)
                authenticated_user_id = user.id.value
                await self._unit_of_work.commit()
        if reused:
            logger.warning(
                "refresh_token_reuse_detected",
                extra={
                    "operation": "refresh_session",
                    "action": "Review the security audit and investigate possible token theft.",
                },
            )
            raise SessionRevokedError("Reutilização de refresh token detectada; sessão revogada.")
        assert result is not None
        assert authenticated_user_id is not None
        logger.info(
            "session_refreshed",
            extra={
                "operation": "refresh_session",
                "user_id": str(authenticated_user_id),
                "action": "No action required.",
            },
        )
        return result
