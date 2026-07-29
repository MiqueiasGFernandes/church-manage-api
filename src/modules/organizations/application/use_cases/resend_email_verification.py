from datetime import timedelta

from modules.organizations.application.ports.auth import (
    IEmailSender,
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
from modules.organizations.domain.model import EmailAddress, UserStatus
from modules.organizations.domain.use_cases.resend_email_verification import (
    IResendEmailVerification,
)


class ResendEmailVerification(IResendEmailVerification):
    def __init__(
        self,
        repository: IAuthRepository,
        unit_of_work: IUnitOfWork,
        tokens: ITokenService,
        email_sender: IEmailSender,
        clock: IClock,
    ) -> None:
        self._repository, self._unit_of_work = repository, unit_of_work
        self._tokens, self._email_sender, self._clock = tokens, email_sender, clock

    async def execute(self, email: str) -> None:
        now = self._clock.now()
        token: str | None = None
        normalized = EmailAddress(email)
        async with self._unit_of_work:
            user = await self._repository.find_user_by_email(normalized)
            if user is not None and user.status is UserStatus.PENDING_EMAIL_VERIFICATION:
                await self._repository.invalidate_email_verifications(user.id.value, now)
                token = self._tokens.generate_opaque()
                await self._repository.add_email_verification(
                    user.id.value,
                    self._tokens.hash_opaque(token),
                    now + timedelta(hours=24),
                )
                await self._repository.add_audit_event(
                    SecurityAuditEvent(
                        "EMAIL_VERIFICATION_REQUESTED", now, target_user_id=user.id.value
                    )
                )
                await self._unit_of_work.commit()
        if token is not None:
            await self._email_sender.send_email_verification(normalized.value, token)
