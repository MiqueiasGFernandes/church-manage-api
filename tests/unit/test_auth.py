from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.container import Container
from app.main import create_app
from modules.organizations.application.dto.register_church import (
    RegisterAddressInput,
    RegisterAdministratorInput,
    RegisterChurchInput,
)
from modules.organizations.application.errors.auth import (
    ChurchAccessDeniedError,
    EmailNotVerifiedError,
    InvalidAccessTokenError,
    InvalidCredentialsError,
    InvalidEmailVerificationTokenError,
    InvalidPasswordError,
    InvalidPasswordResetTokenError,
    RateLimitExceededError,
    SessionRevokedError,
)
from modules.organizations.application.ports.auth import (
    IRateLimiter,
    RateLimitAction,
    RateLimitPolicies,
)
from modules.organizations.application.use_cases.authenticate_user import AuthenticateUser
from modules.organizations.application.use_cases.change_password import ChangePassword
from modules.organizations.application.use_cases.get_current_user import GetCurrentUser
from modules.organizations.application.use_cases.list_user_sessions import ListUserSessions
from modules.organizations.application.use_cases.logout_all_sessions import LogoutAllSessions
from modules.organizations.application.use_cases.logout_session import LogoutSession
from modules.organizations.application.use_cases.password_policy import ensure_valid_password
from modules.organizations.application.use_cases.refresh_session import RefreshSession
from modules.organizations.application.use_cases.register_church import RegisterChurch
from modules.organizations.application.use_cases.request_password_reset import RequestPasswordReset
from modules.organizations.application.use_cases.require_permission import RequirePermission
from modules.organizations.application.use_cases.resend_email_verification import (
    ResendEmailVerification,
)
from modules.organizations.application.use_cases.reset_password import ResetPassword
from modules.organizations.application.use_cases.resolve_access_token import ResolveAccessToken
from modules.organizations.application.use_cases.revoke_user_session import RevokeUserSession
from modules.organizations.application.use_cases.verify_email import VerifyEmail
from modules.organizations.infrastructure.in_memory import (
    Argon2Hasher,
    InMemoryRegistrationRepository,
    InMemoryUnitOfWork,
)
from modules.organizations.infrastructure.security import (
    HmacTokenService,
    InMemoryEmailSender,
)


class SequentialIdGenerator:
    def __init__(self) -> None:
        self._value = 0

    def generate(self) -> UUID:
        self._value += 1
        return UUID(int=self._value)


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 7, 25, tzinfo=UTC)


def valid_input() -> RegisterChurchInput:
    return RegisterChurchInput(
        official_name="Igreja Batista Central de Jundiaí",
        display_name="Igreja Batista Central",
        document="11.222.333/0001-81",
        institutional_email="contato@igreja.com.br",
        institutional_phone="+5511999999999",
        website="https://igreja.com.br",
        slug="igreja-central-jundiai",
        timezone="America/Sao_Paulo",
        address=RegisterAddressInput(
            "13200-000", "Rua das Igrejas", "100", None, "Centro", "Jundiaí", "SP", "BR"
        ),
        administrator=RegisterAdministratorInput(
            "João da Silva",
            "joao@igreja.com.br",
            "+5511999999999",
            "SenhaSegura123",
            "SenhaSegura123",
        ),
        terms_accepted=True,
    )


@pytest.fixture
def auth_flow() -> tuple[
    InMemoryRegistrationRepository,
    InMemoryEmailSender,
    RegisterChurch,
    VerifyEmail,
    AuthenticateUser,
    RefreshSession,
    ResolveAccessToken,
]:
    repository = InMemoryRegistrationRepository()
    clock = FixedClock()
    ids = SequentialIdGenerator()
    passwords = Argon2Hasher()
    tokens = HmacTokenService("test-secret-key-with-at-least-32-characters")
    email = InMemoryEmailSender()
    unit_of_work = InMemoryUnitOfWork(repository)
    return (
        repository,
        email,
        RegisterChurch(repository, unit_of_work, passwords, ids, clock, tokens, email),
        VerifyEmail(repository, unit_of_work, tokens, clock),
        AuthenticateUser(repository, unit_of_work, passwords, tokens, ids, clock),
        RefreshSession(repository, unit_of_work, tokens, clock),
        ResolveAccessToken(repository, unit_of_work, tokens, clock),
    )


async def test_requires_email_verification_before_login_and_token_is_single_use(
    auth_flow: tuple[
        InMemoryRegistrationRepository,
        InMemoryEmailSender,
        RegisterChurch,
        VerifyEmail,
        AuthenticateUser,
        RefreshSession,
        ResolveAccessToken,
    ],
) -> None:
    _, email, register, verify, authenticate, _, _ = auth_flow
    await register.execute(valid_input())

    with pytest.raises(EmailNotVerifiedError):
        await authenticate.execute("joao@igreja.com.br", "SenhaSegura123")

    verification_token = email.verifications[0][1]
    await verify.execute(verification_token)
    with pytest.raises(InvalidEmailVerificationTokenError):
        await verify.execute(verification_token)

    pair = await authenticate.execute("JOAO@IGREJA.COM.BR", "SenhaSegura123")
    assert pair.token_type == "Bearer"
    assert pair.expires_in == 900


async def test_login_is_neutral_and_refresh_token_rotates(
    auth_flow: tuple[
        InMemoryRegistrationRepository,
        InMemoryEmailSender,
        RegisterChurch,
        VerifyEmail,
        AuthenticateUser,
        RefreshSession,
        ResolveAccessToken,
    ],
) -> None:
    repository, email, register, verify, authenticate, refresh, _ = auth_flow
    await register.execute(valid_input())
    await verify.execute(email.verifications[0][1])

    with pytest.raises(InvalidCredentialsError, match="E-mail ou senha inválidos"):
        await authenticate.execute("inexistente@example.com", "SenhaErrada123")
    with pytest.raises(InvalidCredentialsError, match="E-mail ou senha inválidos"):
        await authenticate.execute("joao@igreja.com.br", "SenhaErrada123")
    assert [event.event_type for event in repository.audit_events].count("LOGIN_FAILED") == 2

    original = await authenticate.execute("joao@igreja.com.br", "SenhaSegura123")
    rotated = await refresh.execute(original.refresh_token)
    assert rotated.refresh_token != original.refresh_token
    with pytest.raises(SessionRevokedError):
        await refresh.execute(original.refresh_token)
    assert repository.sessions[0].revoked_at is not None
    assert repository.audit_events[-1].event_type == "SUSPICIOUS_REFRESH_TOKEN_REUSE"


async def test_access_token_resolves_user_and_permissions_are_tenant_scoped(
    auth_flow: tuple[
        InMemoryRegistrationRepository,
        InMemoryEmailSender,
        RegisterChurch,
        VerifyEmail,
        AuthenticateUser,
        RefreshSession,
        ResolveAccessToken,
    ],
) -> None:
    repository, email, register, verify, authenticate, _, resolve = auth_flow
    registration = await register.execute(valid_input())
    await verify.execute(email.verifications[0][1])
    pair = await authenticate.execute("joao@igreja.com.br", "SenhaSegura123")
    actor = await resolve.execute(pair.access_token)

    unit_of_work = InMemoryUnitOfWork(repository)
    current = await GetCurrentUser(repository, unit_of_work).execute(actor)
    assert current.churches[0].role == "church_owner"
    assert "church:configure" in current.churches[0].permissions
    await RequirePermission(repository, unit_of_work, FixedClock()).execute(
        actor, registration.church_id, "church:configure"
    )
    with pytest.raises(ChurchAccessDeniedError):
        await RequirePermission(repository, unit_of_work, FixedClock()).execute(
            actor, UUID(int=999), "church:configure"
        )


async def test_lists_revokes_and_logs_out_all_owned_sessions(
    auth_flow: tuple[
        InMemoryRegistrationRepository,
        InMemoryEmailSender,
        RegisterChurch,
        VerifyEmail,
        AuthenticateUser,
        RefreshSession,
        ResolveAccessToken,
    ],
) -> None:
    repository, email, register, verify, authenticate, _, resolve = auth_flow
    await register.execute(valid_input())
    await verify.execute(email.verifications[0][1])
    first = await authenticate.execute("joao@igreja.com.br", "SenhaSegura123")
    await authenticate.execute("joao@igreja.com.br", "SenhaSegura123")
    actor = await resolve.execute(first.access_token)
    unit_of_work = InMemoryUnitOfWork(repository)

    sessions = await ListUserSessions(repository, unit_of_work, FixedClock()).execute(actor)
    assert len(sessions) == 2
    assert sum(item.current for item in sessions) == 1

    other_session = next(item for item in sessions if not item.current)
    await RevokeUserSession(repository, unit_of_work, FixedClock()).execute(
        actor, other_session.session_id
    )
    assert len(await ListUserSessions(repository, unit_of_work, FixedClock()).execute(actor)) == 1

    await LogoutAllSessions(repository, unit_of_work, FixedClock()).execute(actor)
    with pytest.raises(InvalidAccessTokenError):
        await resolve.execute(first.access_token)
    assert repository.audit_events[-1].event_type == "ALL_SESSIONS_REVOKED"


async def test_rate_limiter_uses_configured_limit_for_authentication_attempts() -> None:
    container = Container()
    container.config.rate_limit_login_limit.from_value(2)
    container.config.rate_limit_login_window_seconds.from_value(60)
    limiter: IRateLimiter = container.rate_limiter()

    for _ in range(2):
        await limiter.ensure_allowed(RateLimitAction.LOGIN, "login:127.0.0.1:user@example.com")

    with pytest.raises(RateLimitExceededError):
        await limiter.ensure_allowed(RateLimitAction.LOGIN, "login:127.0.0.1:user@example.com")


def test_application_loads_rate_limit_policy_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("RATE_LIMIT_LOGIN_LIMIT", "7")
    monkeypatch.setenv("RATE_LIMIT_LOGIN_WINDOW_SECONDS", "90")

    application = create_app()
    policies: RateLimitPolicies = application.state.container.rate_limit_policies()

    assert policies[RateLimitAction.LOGIN].limit == 7
    assert policies[RateLimitAction.LOGIN].window_seconds == 90


async def test_resends_email_verification_and_invalidates_previous_token(
    auth_flow: tuple[
        InMemoryRegistrationRepository,
        InMemoryEmailSender,
        RegisterChurch,
        VerifyEmail,
        AuthenticateUser,
        RefreshSession,
        ResolveAccessToken,
    ],
) -> None:
    repository, email, register, verify, _, _, _ = auth_flow
    await register.execute(valid_input())
    original = email.verifications[-1][1]
    resend = ResendEmailVerification(
        repository,
        InMemoryUnitOfWork(repository),
        HmacTokenService("test-secret-key-with-at-least-32-characters"),
        email,
        FixedClock(),
    )

    await resend.execute("joao@igreja.com.br")

    with pytest.raises(InvalidEmailVerificationTokenError):
        await verify.execute(original)
    await verify.execute(email.verifications[-1][1])


async def test_password_reset_is_neutral_single_use_and_revokes_sessions(
    auth_flow: tuple[
        InMemoryRegistrationRepository,
        InMemoryEmailSender,
        RegisterChurch,
        VerifyEmail,
        AuthenticateUser,
        RefreshSession,
        ResolveAccessToken,
    ],
) -> None:
    repository, email, register, verify, authenticate, _, resolve = auth_flow
    await register.execute(valid_input())
    await verify.execute(email.verifications[-1][1])
    pair = await authenticate.execute("joao@igreja.com.br", "SenhaSegura123")
    tokens = HmacTokenService("test-secret-key-with-at-least-32-characters")
    request_reset = RequestPasswordReset(
        repository, InMemoryUnitOfWork(repository), tokens, email, FixedClock()
    )
    reset = ResetPassword(
        repository, InMemoryUnitOfWork(repository), tokens, Argon2Hasher(), FixedClock()
    )

    await request_reset.execute("inexistente@example.com")
    assert email.password_resets == []
    await request_reset.execute("joao@igreja.com.br")
    reset_token = email.password_resets[-1][1]
    await reset.execute(reset_token, "NovaSenhaSegura123")

    with pytest.raises(InvalidPasswordResetTokenError):
        await reset.execute(reset_token, "OutraSenhaSegura123")
    with pytest.raises(InvalidAccessTokenError):
        await resolve.execute(pair.access_token)
    with pytest.raises(InvalidCredentialsError):
        await authenticate.execute("joao@igreja.com.br", "SenhaSegura123")
    assert (await authenticate.execute("joao@igreja.com.br", "NovaSenhaSegura123")).access_token


async def test_changes_password_and_revokes_other_sessions(
    auth_flow: tuple[
        InMemoryRegistrationRepository,
        InMemoryEmailSender,
        RegisterChurch,
        VerifyEmail,
        AuthenticateUser,
        RefreshSession,
        ResolveAccessToken,
    ],
) -> None:
    repository, email, register, verify, authenticate, _, resolve = auth_flow
    await register.execute(valid_input())
    await verify.execute(email.verifications[-1][1])
    current = await authenticate.execute("joao@igreja.com.br", "SenhaSegura123")
    other = await authenticate.execute("joao@igreja.com.br", "SenhaSegura123")
    actor = await resolve.execute(current.access_token)
    passwords = Argon2Hasher()

    await ChangePassword(
        repository, InMemoryUnitOfWork(repository), passwords, passwords, FixedClock()
    ).execute(actor, "SenhaSegura123", "SenhaAlterada123")

    assert await resolve.execute(current.access_token) == actor
    with pytest.raises(InvalidAccessTokenError):
        await resolve.execute(other.access_token)
    with pytest.raises(InvalidCredentialsError):
        await authenticate.execute("joao@igreja.com.br", "SenhaSegura123")
    assert (await authenticate.execute("joao@igreja.com.br", "SenhaAlterada123")).access_token


async def test_logout_revokes_current_session_and_records_audit_event(
    auth_flow: tuple[
        InMemoryRegistrationRepository,
        InMemoryEmailSender,
        RegisterChurch,
        VerifyEmail,
        AuthenticateUser,
        RefreshSession,
        ResolveAccessToken,
    ],
) -> None:
    repository, email, register, verify, authenticate, _, resolve = auth_flow
    await register.execute(valid_input())
    await verify.execute(email.verifications[-1][1])
    pair = await authenticate.execute("joao@igreja.com.br", "SenhaSegura123")
    actor = await resolve.execute(pair.access_token)

    await LogoutSession(repository, InMemoryUnitOfWork(repository), FixedClock()).execute(actor)

    with pytest.raises(InvalidAccessTokenError):
        await resolve.execute(pair.access_token)
    assert repository.audit_events[-1].event_type == "SESSION_REVOKED"
    assert repository.audit_events[-1].session_id == actor.session_id


async def test_rejects_malformed_tampered_and_expired_access_tokens(
    auth_flow: tuple[
        InMemoryRegistrationRepository,
        InMemoryEmailSender,
        RegisterChurch,
        VerifyEmail,
        AuthenticateUser,
        RefreshSession,
        ResolveAccessToken,
    ],
) -> None:
    _, email, register, verify, authenticate, _, resolve = auth_flow
    await register.execute(valid_input())
    await verify.execute(email.verifications[-1][1])
    pair = await authenticate.execute("joao@igreja.com.br", "SenhaSegura123")
    header, payload, signature = pair.access_token.split(".")
    tampered_signature = ("A" if signature[0] != "A" else "B") + signature[1:]
    tampered_token = f"{header}.{payload}.{tampered_signature}"

    for token in ("not-a-token", f"invalid-header.{payload}.{signature}", tampered_token):
        with pytest.raises(InvalidAccessTokenError):
            await resolve.execute(token)

    expired_tokens = HmacTokenService(
        "test-secret-key-with-at-least-32-characters", access_token_minutes=-1
    )
    expired, _ = expired_tokens.issue_access(UUID(int=1), UUID(int=2), FixedClock().now())
    with pytest.raises(InvalidAccessTokenError):
        await resolve.execute(expired)


def test_rejects_weak_passwords_and_short_token_secret() -> None:
    with pytest.raises(InvalidPasswordError):
        ensure_valid_password("short", "user@example.com")
    with pytest.raises(InvalidPasswordError):
        ensure_valid_password("user@example.com", " USER@example.com ")
    with pytest.raises(ValueError, match="pelo menos 32 caracteres"):
        HmacTokenService("short-secret")
