from datetime import timedelta

from modules.organizations.application.dto.auth import (
    TokenPair,
)
from modules.organizations.application.errors.auth import (
    AuthenticationError,
    EmailNotVerifiedError,
    InvalidCredentialsError,
)
from modules.organizations.application.ports.auth import (
    IPasswordVerifier,
    ITokenService,
)
from modules.organizations.application.ports.registration_services import (
    IClock,
    IIdGenerator,
    IUnitOfWork,
)
from modules.organizations.application.repositories.auth_repository import (
    IAuthRepository,
    SecurityAuditEvent,
)
from modules.organizations.domain.model import EmailAddress, UserStatus
from modules.organizations.domain.use_cases.authenticate_user import IAuthenticateUser


class AuthenticateUser(IAuthenticateUser):
    def __init__(
        self,
        repository: IAuthRepository,
        unit_of_work: IUnitOfWork,
        passwords: IPasswordVerifier,
        tokens: ITokenService,
        ids: IIdGenerator,
        clock: IClock,
    ) -> None:
        self._repository, self._unit_of_work = repository, unit_of_work
        self._passwords, self._tokens, self._ids, self._clock = passwords, tokens, ids, clock

    async def execute(self, email: str, password: str) -> TokenPair:
        now = self._clock.now()
        failure: AuthenticationError | None = None
        result: TokenPair | None = None
        async with self._unit_of_work:
            user = await self._repository.find_user_by_email(EmailAddress(email))
            if user is None or not self._passwords.verify(password, user.password_hash):
                failure = InvalidCredentialsError("E-mail ou senha inválidos.")
            elif user.status is UserStatus.PENDING_EMAIL_VERIFICATION:
                failure = EmailNotVerifiedError("Confirme seu e-mail antes de entrar.")
            elif user.status is not UserStatus.ACTIVE:
                failure = InvalidCredentialsError("E-mail ou senha inválidos.")
            if failure is not None:
                await self._repository.add_audit_event(
                    SecurityAuditEvent(
                        "LOGIN_FAILED",
                        now,
                        target_user_id=user.id.value if user is not None else None,
                    )
                )
                await self._unit_of_work.commit()
            else:
                assert user is not None
                session_id, refresh = self._ids.generate(), self._tokens.generate_opaque()
                await self._repository.add_session(
                    session_id,
                    user.id.value,
                    self._tokens.hash_opaque(refresh),
                    now,
                    now + timedelta(days=14),
                )
                user.record_login(now)
                await self._repository.save_user(user)
                await self._repository.add_audit_event(
                    SecurityAuditEvent(
                        "LOGIN_SUCCEEDED",
                        now,
                        actor_user_id=user.id.value,
                        session_id=session_id,
                    )
                )
                await self._repository.add_audit_event(
                    SecurityAuditEvent(
                        "SESSION_CREATED",
                        now,
                        actor_user_id=user.id.value,
                        session_id=session_id,
                    )
                )
                access, expires_in = self._tokens.issue_access(user.id.value, session_id, now)
                result = TokenPair(access, refresh, expires_in)
                await self._unit_of_work.commit()
        if failure is not None:
            raise failure
        assert result is not None
        return result
