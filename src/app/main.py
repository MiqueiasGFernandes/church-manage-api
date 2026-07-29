import os
import secrets
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.container import Container
from modules.organizations.application.errors.auth import AuthenticationError
from modules.organizations.domain.use_cases.register_church import IRegisterChurch
from modules.organizations.presentation.auth_http import (
    auth_error_handler,
    church_router,
    get_authenticate,
    get_change_password,
    get_current_user,
    get_list_sessions,
    get_logout_all_sessions,
    get_logout_session,
    get_rate_limiter,
    get_refresh_session,
    get_request_password_reset,
    get_require_permission,
    get_resend_email_verification,
    get_reset_password,
    get_resolve_access,
    get_revoke_session,
    get_verify_email,
)
from modules.organizations.presentation.auth_http import (
    router as auth_router,
)
from modules.organizations.presentation.http import (
    HANDLED_ERRORS,
    get_register_church,
    registration_error_handler,
    router,
)


def create_app() -> FastAPI:
    container = Container()
    persistence_backend = os.getenv("PERSISTENCE_BACKEND", "memory")
    database_url = os.getenv("DATABASE_URL", "")
    auth_token_secret = os.getenv("AUTH_TOKEN_SECRET", secrets.token_urlsafe(32))
    auth_cookie_secure = os.getenv("AUTH_COOKIE_SECURE", "false").lower() == "true"
    container.config.persistence_backend.from_value(persistence_backend)
    container.config.database_url.from_value(database_url)
    container.config.auth_token_secret.from_value(auth_token_secret)
    container.config.email_backend.from_value(os.getenv("EMAIL_BACKEND", "memory"))
    container.config.smtp_host.from_value(os.getenv("SMTP_HOST", ""))
    container.config.smtp_port.from_value(os.getenv("SMTP_PORT", "587"))
    container.config.smtp_sender.from_value(os.getenv("SMTP_SENDER", ""))
    container.config.smtp_username.from_value(os.getenv("SMTP_USERNAME", ""))
    container.config.smtp_password.from_value(os.getenv("SMTP_PASSWORD", ""))
    container.config.smtp_use_tls.from_value(os.getenv("SMTP_USE_TLS", "true"))
    container.config.public_app_url.from_value(os.getenv("PUBLIC_APP_URL", ""))
    container.config.rate_limit_verify_email_limit.from_value(
        os.getenv("RATE_LIMIT_VERIFY_EMAIL_LIMIT", "10")
    )
    container.config.rate_limit_verify_email_window_seconds.from_value(
        os.getenv("RATE_LIMIT_VERIFY_EMAIL_WINDOW_SECONDS", "3600")
    )
    container.config.rate_limit_resend_email_verification_limit.from_value(
        os.getenv("RATE_LIMIT_RESEND_EMAIL_VERIFICATION_LIMIT", "5")
    )
    container.config.rate_limit_resend_email_verification_window_seconds.from_value(
        os.getenv("RATE_LIMIT_RESEND_EMAIL_VERIFICATION_WINDOW_SECONDS", "3600")
    )
    container.config.rate_limit_forgot_password_limit.from_value(
        os.getenv("RATE_LIMIT_FORGOT_PASSWORD_LIMIT", "5")
    )
    container.config.rate_limit_forgot_password_window_seconds.from_value(
        os.getenv("RATE_LIMIT_FORGOT_PASSWORD_WINDOW_SECONDS", "3600")
    )
    container.config.rate_limit_reset_password_limit.from_value(
        os.getenv("RATE_LIMIT_RESET_PASSWORD_LIMIT", "10")
    )
    container.config.rate_limit_reset_password_window_seconds.from_value(
        os.getenv("RATE_LIMIT_RESET_PASSWORD_WINDOW_SECONDS", "3600")
    )
    container.config.rate_limit_login_limit.from_value(os.getenv("RATE_LIMIT_LOGIN_LIMIT", "5"))
    container.config.rate_limit_login_window_seconds.from_value(
        os.getenv("RATE_LIMIT_LOGIN_WINDOW_SECONDS", "60")
    )
    container.config.rate_limit_refresh_limit.from_value(
        os.getenv("RATE_LIMIT_REFRESH_LIMIT", "20")
    )
    container.config.rate_limit_refresh_window_seconds.from_value(
        os.getenv("RATE_LIMIT_REFRESH_WINDOW_SECONDS", "60")
    )
    container.config.rate_limit_change_password_limit.from_value(
        os.getenv("RATE_LIMIT_CHANGE_PASSWORD_LIMIT", "5")
    )
    container.config.rate_limit_change_password_window_seconds.from_value(
        os.getenv("RATE_LIMIT_CHANGE_PASSWORD_WINDOW_SECONDS", "3600")
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
        yield
        if persistence_backend == "postgresql":
            await container.database().dispose()

    async def resolve_register_church() -> IRegisterChurch:
        return container.register_church()

    async def resolve_verify_email():
        return container.verify_email()

    async def resolve_authenticate():
        return container.authenticate()

    async def resolve_refresh_session():
        return container.refresh_session()

    async def resolve_access():
        return container.resolve_access()

    async def resolve_current_user():
        return container.current_user()

    async def resolve_logout_session():
        return container.logout_session()

    async def resolve_logout_all_sessions():
        return container.logout_all_sessions()

    async def resolve_list_sessions():
        return container.list_sessions()

    async def resolve_revoke_session():
        return container.revoke_session()

    async def resolve_permission():
        return container.require_permission()

    async def resolve_rate_limiter():
        return container.rate_limiter()

    async def resolve_resend_email_verification():
        return container.resend_email_verification()

    async def resolve_request_password_reset():
        return container.request_password_reset()

    async def resolve_reset_password():
        return container.reset_password()

    async def resolve_change_password():
        return container.change_password()

    application = FastAPI(title="Church Manage API", version="0.1.0", lifespan=lifespan)
    application.state.auth_cookie_secure = auth_cookie_secure
    application.state.container = container
    application.include_router(router)
    application.include_router(auth_router)
    application.include_router(church_router)
    application.dependency_overrides[get_register_church] = resolve_register_church
    application.dependency_overrides[get_verify_email] = resolve_verify_email
    application.dependency_overrides[get_authenticate] = resolve_authenticate
    application.dependency_overrides[get_refresh_session] = resolve_refresh_session
    application.dependency_overrides[get_resolve_access] = resolve_access
    application.dependency_overrides[get_current_user] = resolve_current_user
    application.dependency_overrides[get_logout_session] = resolve_logout_session
    application.dependency_overrides[get_logout_all_sessions] = resolve_logout_all_sessions
    application.dependency_overrides[get_list_sessions] = resolve_list_sessions
    application.dependency_overrides[get_revoke_session] = resolve_revoke_session
    application.dependency_overrides[get_require_permission] = resolve_permission
    application.dependency_overrides[get_rate_limiter] = resolve_rate_limiter
    application.dependency_overrides[get_resend_email_verification] = (
        resolve_resend_email_verification
    )
    application.dependency_overrides[get_request_password_reset] = resolve_request_password_reset
    application.dependency_overrides[get_reset_password] = resolve_reset_password
    application.dependency_overrides[get_change_password] = resolve_change_password
    for error_type in HANDLED_ERRORS:
        application.add_exception_handler(error_type, registration_error_handler)
    application.add_exception_handler(AuthenticationError, auth_error_handler)
    return application


app = create_app()
