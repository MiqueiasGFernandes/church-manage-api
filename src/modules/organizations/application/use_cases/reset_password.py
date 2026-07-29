import logging

from modules.organizations.application.errors.auth import (
    InvalidPasswordResetTokenError,
)
from modules.organizations.application.ports.auth import (
    ITokenService,
)
from modules.organizations.application.ports.registration_services import (
    IClock,
    IPasswordHasher,
    IUnitOfWork,
)
from modules.organizations.application.repositories.auth_repository import (
    IAuthRepository,
    SecurityAuditEvent,
)
from modules.organizations.application.use_cases.password_policy import ensure_valid_password
from modules.organizations.domain.model import UserStatus
from modules.organizations.domain.use_cases.reset_password import IResetPassword

logger = logging.getLogger(f"church_manage.{__name__}")


class ResetPassword(IResetPassword):
    def __init__(
        self,
        repository: IAuthRepository,
        unit_of_work: IUnitOfWork,
        tokens: ITokenService,
        passwords: IPasswordHasher,
        clock: IClock,
    ) -> None:
        self._repository, self._unit_of_work = repository, unit_of_work
        self._tokens, self._passwords, self._clock = tokens, passwords, clock

    async def execute(self, token: str, new_password: str) -> None:
        now = self._clock.now()
        token_hash = self._tokens.hash_opaque(token)
        async with self._unit_of_work:
            record = await self._repository.find_password_reset(token_hash)
            if record is None or record.used_at is not None or record.expires_at <= now:
                raise InvalidPasswordResetTokenError("Token de redefinição inválido ou expirado.")
            user = await self._repository.find_user_by_id(record.user_id)
            if user is None or user.status is not UserStatus.ACTIVE:
                raise InvalidPasswordResetTokenError("Token de redefinição inválido ou expirado.")
            ensure_valid_password(new_password, user.email.value)
            user.change_password(self._passwords.hash(new_password), now)
            await self._repository.save_user(user)
            await self._repository.use_password_reset(token_hash, now)
            for session in await self._repository.sessions_for_user(user.id.value):
                if session.revoked_at is None:
                    await self._repository.revoke_session(session.id, now)
            await self._repository.add_audit_event(
                SecurityAuditEvent("PASSWORD_RESET_SUCCEEDED", now, actor_user_id=user.id.value)
            )
            await self._unit_of_work.commit()
        logger.info(
            "password_reset_completed",
            extra={
                "operation": "reset_password",
                "user_id": str(user.id.value),
                "action": "No action required.",
            },
        )
