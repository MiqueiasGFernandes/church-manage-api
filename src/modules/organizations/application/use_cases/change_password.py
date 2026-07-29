import logging

from modules.organizations.application.dto.auth import (
    AuthenticatedUser,
)
from modules.organizations.application.errors.auth import (
    InvalidCredentialsError,
)
from modules.organizations.application.ports.auth import (
    IPasswordVerifier,
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
from modules.organizations.domain.use_cases.change_password import IChangePassword

logger = logging.getLogger(f"church_manage.{__name__}")


class ChangePassword(IChangePassword):
    def __init__(
        self,
        repository: IAuthRepository,
        unit_of_work: IUnitOfWork,
        verifier: IPasswordVerifier,
        hasher: IPasswordHasher,
        clock: IClock,
    ) -> None:
        self._repository, self._unit_of_work = repository, unit_of_work
        self._verifier, self._hasher, self._clock = verifier, hasher, clock

    async def execute(
        self, actor: AuthenticatedUser, current_password: str, new_password: str
    ) -> None:
        now = self._clock.now()
        invalid_current = False
        async with self._unit_of_work:
            user = await self._repository.find_user_by_id(actor.user_id)
            if user is None or not self._verifier.verify(current_password, user.password_hash):
                invalid_current = True
            else:
                ensure_valid_password(new_password, user.email.value)
                user.change_password(self._hasher.hash(new_password), now)
                await self._repository.save_user(user)
                for session in await self._repository.sessions_for_user(user.id.value):
                    if session.revoked_at is None and session.id != actor.session_id:
                        await self._repository.revoke_session(session.id, now)
                await self._repository.add_audit_event(
                    SecurityAuditEvent(
                        "PASSWORD_CHANGE_SUCCEEDED",
                        now,
                        actor_user_id=user.id.value,
                        session_id=actor.session_id,
                    )
                )
                await self._unit_of_work.commit()
        if invalid_current:
            raise InvalidCredentialsError("Senha atual inválida.")
        logger.info(
            "password_changed",
            extra={
                "operation": "change_password",
                "user_id": str(actor.user_id),
                "action": "No action required.",
            },
        )
