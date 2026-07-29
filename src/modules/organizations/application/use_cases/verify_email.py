import logging

from modules.organizations.application.errors.auth import (
    InvalidEmailVerificationTokenError,
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
from modules.organizations.domain.use_cases.verify_email import IVerifyEmail

logger = logging.getLogger(f"church_manage.{__name__}")


class VerifyEmail(IVerifyEmail):
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

    async def execute(self, token: str) -> None:
        now = self._clock.now()
        token_hash = self._tokens.hash_opaque(token)
        async with self._unit_of_work:
            record = await self._repository.find_email_verification(token_hash)
            if record is None or record.used_at is not None or record.expires_at <= now:
                raise InvalidEmailVerificationTokenError(
                    "Token de verificação inválido ou expirado."
                )
            user = await self._repository.find_user_by_id(record.user_id)
            if user is None:
                raise InvalidEmailVerificationTokenError(
                    "Token de verificação inválido ou expirado."
                )
            user.verify_email(now)
            await self._repository.save_user(user)
            for membership in await self._repository.memberships_for_user(user.id.value):
                membership.activate()
                await self._repository.save_membership(membership)
            await self._repository.use_email_verification(token_hash, now)
            await self._repository.add_audit_event(
                SecurityAuditEvent("EMAIL_VERIFIED", now, actor_user_id=user.id.value)
            )
            await self._unit_of_work.commit()
        logger.info(
            "email_verified",
            extra={
                "operation": "verify_email",
                "user_id": str(user.id.value),
                "action": "No action required.",
            },
        )
