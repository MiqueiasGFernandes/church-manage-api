import os
import secrets
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.container import Container
from app.observability import bind_request_id, configure_logging, get_logger, reset_request_id
from app.security import SecurityHeadersMiddleware
from app.settings import (
    AppEnvironment,
    CorsSettings,
    ProductionSecuritySettings,
    parse_boolean,
    parse_environment,
)
from modules.organizations.application.errors.auth import AuthenticationError
from modules.organizations.domain.use_cases.register_church import IRegisterChurch
from modules.organizations.presentation.auth_http import (
    auth_error_handler,
    church_router,
    get_authenticate,
    get_change_password,
    get_current_user,
    get_human_challenge_verifier,
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
    environment = parse_environment(os.getenv("APP_ENV", "development"))
    configure_logging(os.getenv("LOG_LEVEL", "INFO"))
    logger = get_logger(__name__)
    persistence_backend = os.getenv("PERSISTENCE_BACKEND", "memory")
    database_url = os.getenv("DATABASE_URL", "")
    configured_auth_token_secret = os.getenv("AUTH_TOKEN_SECRET")
    auth_token_secret = configured_auth_token_secret or secrets.token_urlsafe(32)
    auth_cookie_secure = os.getenv("AUTH_COOKIE_SECURE", "false").lower() == "true"
    email_backend = os.getenv("EMAIL_BACKEND", "memory")
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_sender = os.getenv("SMTP_SENDER", "")
    smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    public_app_url = os.getenv("PUBLIC_APP_URL", "")
    turnstile_enabled = parse_boolean(os.getenv("TURNSTILE_ENABLED", "false"), "TURNSTILE_ENABLED")
    turnstile_secret = os.getenv("TURNSTILE_SECRET", "")
    turnstile_allowed_hostnames = tuple(
        hostname.strip()
        for hostname in os.getenv("TURNSTILE_ALLOWED_HOSTNAMES", "localhost").split(",")
        if hostname.strip()
    )
    cors_settings = CorsSettings.from_strings(
        origins=os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000"),
        methods=os.getenv("CORS_ALLOWED_METHODS", "GET,POST,DELETE,OPTIONS"),
        headers=os.getenv("CORS_ALLOWED_HEADERS", "Authorization,Content-Type"),
        allow_credentials=parse_boolean(
            os.getenv("CORS_ALLOW_CREDENTIALS", "true"), "CORS_ALLOW_CREDENTIALS"
        ),
    )
    allowed_hosts = tuple(
        host.strip()
        for host in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver,test").split(",")
        if host.strip()
    )
    if not allowed_hosts:
        raise ValueError("ALLOWED_HOSTS deve possuir ao menos um valor.")
    api_docs_enabled = parse_boolean(
        os.getenv(
            "API_DOCS_ENABLED",
            "false" if environment is AppEnvironment.PRODUCTION else "true",
        ),
        "API_DOCS_ENABLED",
    )
    if environment is AppEnvironment.PRODUCTION:
        ProductionSecuritySettings(
            persistence_backend=persistence_backend,
            database_url=database_url,
            auth_token_secret=configured_auth_token_secret,
            auth_cookie_secure=auth_cookie_secure,
            email_backend=email_backend,
            smtp_host=smtp_host,
            smtp_sender=smtp_sender,
            smtp_use_tls=smtp_use_tls,
            public_app_url=public_app_url,
            cors_allowed_origins=cors_settings.allowed_origins,
            cors_allow_credentials=cors_settings.allow_credentials,
            allowed_hosts=allowed_hosts,
            turnstile_enabled=turnstile_enabled,
            turnstile_secret=turnstile_secret,
            turnstile_allowed_hostnames=turnstile_allowed_hostnames,
        ).validate()
    container.config.persistence_backend.from_value(persistence_backend)
    container.config.database_url.from_value(database_url)
    container.config.auth_token_secret.from_value(auth_token_secret)
    container.config.email_backend.from_value(email_backend)
    container.config.smtp_host.from_value(smtp_host)
    container.config.smtp_port.from_value(os.getenv("SMTP_PORT", "587"))
    container.config.smtp_sender.from_value(smtp_sender)
    container.config.smtp_username.from_value(os.getenv("SMTP_USERNAME", ""))
    container.config.smtp_password.from_value(os.getenv("SMTP_PASSWORD", ""))
    container.config.smtp_use_tls.from_value(str(smtp_use_tls).lower())
    container.config.public_app_url.from_value(public_app_url)
    container.config.turnstile_enabled.from_value(str(turnstile_enabled).lower())
    container.config.turnstile_secret.from_value(turnstile_secret)
    container.config.turnstile_allowed_hostnames.from_value(turnstile_allowed_hostnames)
    container.config.rate_limit_register_church_limit.from_value(
        os.getenv("RATE_LIMIT_REGISTER_CHURCH_LIMIT", "5")
    )
    container.config.rate_limit_register_church_window_seconds.from_value(
        os.getenv("RATE_LIMIT_REGISTER_CHURCH_WINDOW_SECONDS", "3600")
    )
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
        logger.info(
            "application_started",
            extra={
                "operation": "application_lifecycle",
                "environment": environment.value,
                "persistence_backend": persistence_backend,
                "action": "No action required.",
            },
        )
        try:
            yield
        finally:
            await container.http_client().aclose()
            if persistence_backend == "postgresql":
                await container.database().dispose()
            logger.info(
                "application_stopped",
                extra={
                    "operation": "application_lifecycle",
                    "environment": environment.value,
                    "action": "No action required.",
                },
            )

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

    async def resolve_human_challenge_verifier():
        return container.human_challenge_verifier()

    async def resolve_resend_email_verification():
        return container.resend_email_verification()

    async def resolve_request_password_reset():
        return container.request_password_reset()

    async def resolve_reset_password():
        return container.reset_password()

    async def resolve_change_password():
        return container.change_password()

    documentation_url = "/docs" if api_docs_enabled else None
    redoc_url = "/redoc" if api_docs_enabled else None
    openapi_url = "/openapi.json" if api_docs_enabled else None
    application = FastAPI(
        title="Reuniva API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=documentation_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )

    async def log_request(request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path == "/health":
            return await call_next(request)

        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        request_id_token = bind_request_id(request_id)
        started_at = time.perf_counter()
        context: dict[str, object] = {
            "request_id": request_id,
            "operation": "http_request",
            "method": request.method,
            "path": request.url.path,
        }
        try:
            try:
                response = await call_next(request)
            except Exception:
                logger.exception(
                    "http_request_failed_unexpectedly",
                    extra={
                        **context,
                        "duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
                        "action": (
                            "Inspect the exception and request context, then correct or mitigate "
                            "the failure."
                        ),
                    },
                )
                raise

            response.headers["X-Request-ID"] = request_id
            log_method = logger.warning if response.status_code >= 400 else logger.info
            action = (
                "Review the error code and request context before retrying the operation."
                if response.status_code >= 400
                else "No action required."
            )
            error_code = getattr(request.state, "error_code", None)
            log_method(
                "http_request_completed",
                extra={
                    **context,
                    "status_code": response.status_code,
                    **({"error_code": error_code} if isinstance(error_code, str) else {}),
                    "duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
                    "action": action,
                },
            )
            return response
        finally:
            reset_request_id(request_id_token)

    application.middleware("http")(log_request)

    async def _health() -> Response:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    application.add_api_route(
        "/health",
        _health,
        methods=["GET"],
        status_code=status.HTTP_204_NO_CONTENT,
        response_class=Response,
        include_in_schema=False,
    )

    application.state.auth_cookie_secure = auth_cookie_secure
    application.state.cors_allowed_origins = cors_settings.allowed_origins
    application.state.container = container
    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=list(allowed_hosts),
    )
    application.add_middleware(
        SecurityHeadersMiddleware,
        enable_hsts=environment is AppEnvironment.PRODUCTION,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(cors_settings.allowed_origins),
        allow_credentials=cors_settings.allow_credentials,
        allow_methods=list(cors_settings.allowed_methods),
        allow_headers=list(cors_settings.allowed_headers),
    )
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
    application.dependency_overrides[get_human_challenge_verifier] = (
        resolve_human_challenge_verifier
    )
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
