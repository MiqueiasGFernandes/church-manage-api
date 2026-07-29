from dependency_injector import containers, providers

from modules.organizations.application.ports.auth import (
    IEmailSender,
    RateLimitAction,
    RateLimitPolicy,
)
from modules.organizations.application.use_cases.authenticate_user import AuthenticateUser
from modules.organizations.application.use_cases.change_password import ChangePassword
from modules.organizations.application.use_cases.get_current_user import GetCurrentUser
from modules.organizations.application.use_cases.list_user_sessions import ListUserSessions
from modules.organizations.application.use_cases.logout_all_sessions import LogoutAllSessions
from modules.organizations.application.use_cases.logout_session import LogoutSession
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
    SystemClock,
    UuidGenerator,
)
from modules.organizations.infrastructure.persistence.auth_repository import (
    SqlAlchemyAuthRepository,
)
from modules.organizations.infrastructure.persistence.database import PostgresDatabase
from modules.organizations.infrastructure.persistence.rate_limiter import (
    PostgresFixedWindowRateLimiter,
)
from modules.organizations.infrastructure.persistence.registration_repository import (
    SqlAlchemyRegistrationRepository,
)
from modules.organizations.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from modules.organizations.infrastructure.security import (
    FixedWindowRateLimiter,
    HmacTokenService,
    InMemoryEmailSender,
    SmtpEmailSender,
)


def parse_bool(value: str) -> bool:
    return value.lower() == "true"


def build_rate_limit_policies(
    verify_email_limit: int,
    verify_email_window_seconds: int,
    resend_email_verification_limit: int,
    resend_email_verification_window_seconds: int,
    forgot_password_limit: int,
    forgot_password_window_seconds: int,
    reset_password_limit: int,
    reset_password_window_seconds: int,
    login_limit: int,
    login_window_seconds: int,
    refresh_limit: int,
    refresh_window_seconds: int,
    change_password_limit: int,
    change_password_window_seconds: int,
) -> dict[RateLimitAction, RateLimitPolicy]:
    return {
        RateLimitAction.VERIFY_EMAIL: RateLimitPolicy(
            verify_email_limit, verify_email_window_seconds
        ),
        RateLimitAction.RESEND_EMAIL_VERIFICATION: RateLimitPolicy(
            resend_email_verification_limit, resend_email_verification_window_seconds
        ),
        RateLimitAction.FORGOT_PASSWORD: RateLimitPolicy(
            forgot_password_limit, forgot_password_window_seconds
        ),
        RateLimitAction.RESET_PASSWORD: RateLimitPolicy(
            reset_password_limit, reset_password_window_seconds
        ),
        RateLimitAction.LOGIN: RateLimitPolicy(login_limit, login_window_seconds),
        RateLimitAction.REFRESH: RateLimitPolicy(refresh_limit, refresh_window_seconds),
        RateLimitAction.CHANGE_PASSWORD: RateLimitPolicy(
            change_password_limit, change_password_window_seconds
        ),
    }


def build_postgres_register_church(
    database: PostgresDatabase,
    password_hasher: Argon2Hasher,
    id_generator: UuidGenerator,
    clock: SystemClock,
    token_service: HmacTokenService,
    email_sender: IEmailSender,
) -> RegisterChurch:
    session = database.create_session()
    repository = SqlAlchemyRegistrationRepository(session)
    return RegisterChurch(
        repository=repository,
        unit_of_work=SqlAlchemyUnitOfWork(session),
        password_hasher=password_hasher,
        id_generator=id_generator,
        clock=clock,
        token_service=token_service,
        email_sender=email_sender,
    )


def build_postgres_auth(
    database: PostgresDatabase,
    kind: str,
    password_hasher: Argon2Hasher,
    token_service: HmacTokenService,
    id_generator: UuidGenerator,
    clock: SystemClock,
    email_sender: IEmailSender | None = None,
) -> object:
    session = database.create_session()
    repository = SqlAlchemyAuthRepository(session)
    unit_of_work = SqlAlchemyUnitOfWork(session)
    if kind == "verify":
        return VerifyEmail(repository, unit_of_work, token_service, clock)
    if kind == "authenticate":
        return AuthenticateUser(
            repository, unit_of_work, password_hasher, token_service, id_generator, clock
        )
    if kind == "refresh":
        return RefreshSession(repository, unit_of_work, token_service, clock)
    if kind == "resolve":
        return ResolveAccessToken(repository, unit_of_work, token_service, clock)
    if kind == "current":
        return GetCurrentUser(repository, unit_of_work)
    if kind == "logout":
        return LogoutSession(repository, unit_of_work, clock)
    if kind == "logout_all":
        return LogoutAllSessions(repository, unit_of_work, clock)
    if kind == "list_sessions":
        return ListUserSessions(repository, unit_of_work, clock)
    if kind == "revoke_session":
        return RevokeUserSession(repository, unit_of_work, clock)
    if kind == "resend_verification":
        assert email_sender is not None
        return ResendEmailVerification(repository, unit_of_work, token_service, email_sender, clock)
    if kind == "request_reset":
        assert email_sender is not None
        return RequestPasswordReset(repository, unit_of_work, token_service, email_sender, clock)
    if kind == "reset_password":
        return ResetPassword(repository, unit_of_work, token_service, password_hasher, clock)
    if kind == "change_password":
        return ChangePassword(repository, unit_of_work, password_hasher, password_hasher, clock)
    return RequirePermission(repository, unit_of_work, clock)


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.persistence_backend.from_value("memory")
    config.database_url.from_value("")
    config.auth_token_secret.from_value("development-only-token-secret-32-bytes")
    config.email_backend.from_value("memory")
    config.rate_limit_verify_email_limit.from_value(10)
    config.rate_limit_verify_email_window_seconds.from_value(3600)
    config.rate_limit_resend_email_verification_limit.from_value(5)
    config.rate_limit_resend_email_verification_window_seconds.from_value(3600)
    config.rate_limit_forgot_password_limit.from_value(5)
    config.rate_limit_forgot_password_window_seconds.from_value(3600)
    config.rate_limit_reset_password_limit.from_value(10)
    config.rate_limit_reset_password_window_seconds.from_value(3600)
    config.rate_limit_login_limit.from_value(5)
    config.rate_limit_login_window_seconds.from_value(60)
    config.rate_limit_refresh_limit.from_value(20)
    config.rate_limit_refresh_window_seconds.from_value(60)
    config.rate_limit_change_password_limit.from_value(5)
    config.rate_limit_change_password_window_seconds.from_value(3600)

    repository = providers.Singleton(InMemoryRegistrationRepository)
    unit_of_work = providers.Factory(InMemoryUnitOfWork, repository=repository)
    password_hasher = providers.Singleton(Argon2Hasher)
    id_generator = providers.Singleton(UuidGenerator)
    clock = providers.Singleton(SystemClock)
    rate_limit_policies = providers.Singleton(
        build_rate_limit_policies,
        verify_email_limit=config.rate_limit_verify_email_limit.as_int(),
        verify_email_window_seconds=config.rate_limit_verify_email_window_seconds.as_int(),
        resend_email_verification_limit=config.rate_limit_resend_email_verification_limit.as_int(),
        resend_email_verification_window_seconds=config.rate_limit_resend_email_verification_window_seconds.as_int(),
        forgot_password_limit=config.rate_limit_forgot_password_limit.as_int(),
        forgot_password_window_seconds=config.rate_limit_forgot_password_window_seconds.as_int(),
        reset_password_limit=config.rate_limit_reset_password_limit.as_int(),
        reset_password_window_seconds=config.rate_limit_reset_password_window_seconds.as_int(),
        login_limit=config.rate_limit_login_limit.as_int(),
        login_window_seconds=config.rate_limit_login_window_seconds.as_int(),
        refresh_limit=config.rate_limit_refresh_limit.as_int(),
        refresh_window_seconds=config.rate_limit_refresh_window_seconds.as_int(),
        change_password_limit=config.rate_limit_change_password_limit.as_int(),
        change_password_window_seconds=config.rate_limit_change_password_window_seconds.as_int(),
    )
    in_memory_rate_limiter = providers.Singleton(
        FixedWindowRateLimiter, clock=clock, policies=rate_limit_policies
    )
    token_service = providers.Singleton(HmacTokenService, secret=config.auth_token_secret)
    in_memory_email_sender = providers.Singleton(InMemoryEmailSender)
    smtp_email_sender = providers.Singleton(
        SmtpEmailSender,
        host=config.smtp_host,
        port=config.smtp_port.as_int(),
        sender=config.smtp_sender,
        public_url=config.public_app_url,
        username=config.smtp_username,
        password=config.smtp_password,
        use_tls=config.smtp_use_tls.as_(parse_bool),
    )
    email_sender = providers.Selector(
        config.email_backend, memory=in_memory_email_sender, smtp=smtp_email_sender
    )
    in_memory_register_church = providers.Factory(
        RegisterChurch,
        repository=repository,
        unit_of_work=unit_of_work,
        password_hasher=password_hasher,
        id_generator=id_generator,
        clock=clock,
        token_service=token_service,
        email_sender=email_sender,
    )
    database = providers.Singleton(PostgresDatabase, database_url=config.database_url)
    postgres_rate_limiter = providers.Singleton(
        PostgresFixedWindowRateLimiter,
        database=database,
        clock=clock,
        policies=rate_limit_policies,
    )
    rate_limiter = providers.Selector(
        config.persistence_backend,
        memory=in_memory_rate_limiter,
        postgresql=postgres_rate_limiter,
    )
    postgres_register_church = providers.Factory(
        build_postgres_register_church,
        database=database,
        password_hasher=password_hasher,
        id_generator=id_generator,
        clock=clock,
        token_service=token_service,
        email_sender=email_sender,
    )
    register_church = providers.Selector(
        config.persistence_backend,
        memory=in_memory_register_church,
        postgresql=postgres_register_church,
    )
    in_memory_verify_email = providers.Factory(
        VerifyEmail,
        repository=repository,
        unit_of_work=unit_of_work,
        tokens=token_service,
        clock=clock,
    )
    in_memory_authenticate = providers.Factory(
        AuthenticateUser,
        repository=repository,
        unit_of_work=unit_of_work,
        passwords=password_hasher,
        tokens=token_service,
        ids=id_generator,
        clock=clock,
    )
    in_memory_refresh = providers.Factory(
        RefreshSession,
        repository=repository,
        unit_of_work=unit_of_work,
        tokens=token_service,
        clock=clock,
    )
    in_memory_resolve = providers.Factory(
        ResolveAccessToken,
        repository=repository,
        unit_of_work=unit_of_work,
        tokens=token_service,
        clock=clock,
    )
    in_memory_current = providers.Factory(
        GetCurrentUser, repository=repository, unit_of_work=unit_of_work
    )
    in_memory_logout = providers.Factory(
        LogoutSession, repository=repository, unit_of_work=unit_of_work, clock=clock
    )
    in_memory_logout_all = providers.Factory(
        LogoutAllSessions, repository=repository, unit_of_work=unit_of_work, clock=clock
    )
    in_memory_list_sessions = providers.Factory(
        ListUserSessions, repository=repository, unit_of_work=unit_of_work, clock=clock
    )
    in_memory_revoke_session = providers.Factory(
        RevokeUserSession, repository=repository, unit_of_work=unit_of_work, clock=clock
    )
    in_memory_resend_verification = providers.Factory(
        ResendEmailVerification,
        repository=repository,
        unit_of_work=unit_of_work,
        tokens=token_service,
        email_sender=email_sender,
        clock=clock,
    )
    in_memory_request_reset = providers.Factory(
        RequestPasswordReset,
        repository=repository,
        unit_of_work=unit_of_work,
        tokens=token_service,
        email_sender=email_sender,
        clock=clock,
    )
    in_memory_reset_password = providers.Factory(
        ResetPassword,
        repository=repository,
        unit_of_work=unit_of_work,
        tokens=token_service,
        passwords=password_hasher,
        clock=clock,
    )
    in_memory_change_password = providers.Factory(
        ChangePassword,
        repository=repository,
        unit_of_work=unit_of_work,
        verifier=password_hasher,
        hasher=password_hasher,
        clock=clock,
    )
    in_memory_permission = providers.Factory(
        RequirePermission, repository=repository, unit_of_work=unit_of_work, clock=clock
    )
    postgres_verify_email = providers.Factory(
        build_postgres_auth,
        database=database,
        kind="verify",
        password_hasher=password_hasher,
        token_service=token_service,
        id_generator=id_generator,
        clock=clock,
    )
    postgres_authenticate = providers.Factory(
        build_postgres_auth,
        database=database,
        kind="authenticate",
        password_hasher=password_hasher,
        token_service=token_service,
        id_generator=id_generator,
        clock=clock,
    )
    postgres_refresh = providers.Factory(
        build_postgres_auth,
        database=database,
        kind="refresh",
        password_hasher=password_hasher,
        token_service=token_service,
        id_generator=id_generator,
        clock=clock,
    )
    postgres_resolve = providers.Factory(
        build_postgres_auth,
        database=database,
        kind="resolve",
        password_hasher=password_hasher,
        token_service=token_service,
        id_generator=id_generator,
        clock=clock,
    )
    postgres_current = providers.Factory(
        build_postgres_auth,
        database=database,
        kind="current",
        password_hasher=password_hasher,
        token_service=token_service,
        id_generator=id_generator,
        clock=clock,
    )
    postgres_logout = providers.Factory(
        build_postgres_auth,
        database=database,
        kind="logout",
        password_hasher=password_hasher,
        token_service=token_service,
        id_generator=id_generator,
        clock=clock,
    )
    postgres_logout_all = providers.Factory(
        build_postgres_auth,
        database=database,
        kind="logout_all",
        password_hasher=password_hasher,
        token_service=token_service,
        id_generator=id_generator,
        clock=clock,
    )
    postgres_list_sessions = providers.Factory(
        build_postgres_auth,
        database=database,
        kind="list_sessions",
        password_hasher=password_hasher,
        token_service=token_service,
        id_generator=id_generator,
        clock=clock,
    )
    postgres_revoke_session = providers.Factory(
        build_postgres_auth,
        database=database,
        kind="revoke_session",
        password_hasher=password_hasher,
        token_service=token_service,
        id_generator=id_generator,
        clock=clock,
    )
    postgres_resend_verification = providers.Factory(
        build_postgres_auth,
        database=database,
        kind="resend_verification",
        password_hasher=password_hasher,
        token_service=token_service,
        id_generator=id_generator,
        clock=clock,
        email_sender=email_sender,
    )
    postgres_request_reset = providers.Factory(
        build_postgres_auth,
        database=database,
        kind="request_reset",
        password_hasher=password_hasher,
        token_service=token_service,
        id_generator=id_generator,
        clock=clock,
        email_sender=email_sender,
    )
    postgres_reset_password = providers.Factory(
        build_postgres_auth,
        database=database,
        kind="reset_password",
        password_hasher=password_hasher,
        token_service=token_service,
        id_generator=id_generator,
        clock=clock,
        email_sender=email_sender,
    )
    postgres_change_password = providers.Factory(
        build_postgres_auth,
        database=database,
        kind="change_password",
        password_hasher=password_hasher,
        token_service=token_service,
        id_generator=id_generator,
        clock=clock,
        email_sender=email_sender,
    )
    postgres_permission = providers.Factory(
        build_postgres_auth,
        database=database,
        kind="permission",
        password_hasher=password_hasher,
        token_service=token_service,
        id_generator=id_generator,
        clock=clock,
    )
    verify_email = providers.Selector(
        config.persistence_backend, memory=in_memory_verify_email, postgresql=postgres_verify_email
    )
    authenticate = providers.Selector(
        config.persistence_backend, memory=in_memory_authenticate, postgresql=postgres_authenticate
    )
    refresh_session = providers.Selector(
        config.persistence_backend, memory=in_memory_refresh, postgresql=postgres_refresh
    )
    resolve_access = providers.Selector(
        config.persistence_backend, memory=in_memory_resolve, postgresql=postgres_resolve
    )
    current_user = providers.Selector(
        config.persistence_backend, memory=in_memory_current, postgresql=postgres_current
    )
    logout_session = providers.Selector(
        config.persistence_backend, memory=in_memory_logout, postgresql=postgres_logout
    )
    logout_all_sessions = providers.Selector(
        config.persistence_backend, memory=in_memory_logout_all, postgresql=postgres_logout_all
    )
    list_sessions = providers.Selector(
        config.persistence_backend,
        memory=in_memory_list_sessions,
        postgresql=postgres_list_sessions,
    )
    revoke_session = providers.Selector(
        config.persistence_backend,
        memory=in_memory_revoke_session,
        postgresql=postgres_revoke_session,
    )
    resend_email_verification = providers.Selector(
        config.persistence_backend,
        memory=in_memory_resend_verification,
        postgresql=postgres_resend_verification,
    )
    request_password_reset = providers.Selector(
        config.persistence_backend,
        memory=in_memory_request_reset,
        postgresql=postgres_request_reset,
    )
    reset_password = providers.Selector(
        config.persistence_backend,
        memory=in_memory_reset_password,
        postgresql=postgres_reset_password,
    )
    change_password = providers.Selector(
        config.persistence_backend,
        memory=in_memory_change_password,
        postgresql=postgres_change_password,
    )
    require_permission = providers.Selector(
        config.persistence_backend, memory=in_memory_permission, postgresql=postgres_permission
    )
