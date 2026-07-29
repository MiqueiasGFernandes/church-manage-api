from datetime import UTC, datetime
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app
from modules.organizations.application.use_cases.authenticate_user import AuthenticateUser
from modules.organizations.application.use_cases.get_current_user import GetCurrentUser
from modules.organizations.application.use_cases.list_user_sessions import ListUserSessions
from modules.organizations.application.use_cases.logout_all_sessions import LogoutAllSessions
from modules.organizations.application.use_cases.logout_session import LogoutSession
from modules.organizations.application.use_cases.refresh_session import RefreshSession
from modules.organizations.application.use_cases.register_church import RegisterChurch
from modules.organizations.application.use_cases.require_permission import RequirePermission
from modules.organizations.application.use_cases.resolve_access_token import ResolveAccessToken
from modules.organizations.application.use_cases.revoke_user_session import RevokeUserSession
from modules.organizations.application.use_cases.verify_email import VerifyEmail
from modules.organizations.infrastructure.in_memory import (
    InMemoryRegistrationRepository,
    InMemoryUnitOfWork,
)
from modules.organizations.infrastructure.security import HmacTokenService, InMemoryEmailSender
from modules.organizations.presentation.auth_http import (
    get_authenticate,
    get_current_user,
    get_list_sessions,
    get_logout_all_sessions,
    get_logout_session,
    get_refresh_session,
    get_require_permission,
    get_resolve_access,
    get_revoke_session,
    get_verify_email,
)
from modules.organizations.presentation.http import get_register_church


class SequentialIdGenerator:
    def __init__(self) -> None:
        self._value = 100

    def generate(self) -> UUID:
        self._value += 1
        return UUID(int=self._value)


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 7, 26, tzinfo=UTC)


class FakePasswordHasher:
    def hash(self, plain_text: str) -> str:
        return f"hashed:{plain_text}"

    def verify(self, plain_text: str, password_hash: str) -> bool:
        return password_hash == f"hashed:{plain_text}"


def registration_payload() -> dict[str, object]:
    return {
        "official_name": "Igreja Batista Central de Jundiaí",
        "display_name": "Igreja Batista Central",
        "document": "11.222.333/0001-81",
        "institutional_email": "contato@igreja.com.br",
        "institutional_phone": "+5511999999999",
        "website": "https://igreja.com.br",
        "slug": "igreja-central-jundiai",
        "timezone": "America/Sao_Paulo",
        "address": {
            "postal_code": "13200-000",
            "street": "Rua das Igrejas",
            "number": "100",
            "complement": None,
            "district": "Centro",
            "city": "Jundiaí",
            "state": "SP",
            "country": "BR",
        },
        "administrator": {
            "name": "João da Silva",
            "email": "joao@igreja.com.br",
            "phone": "+5511999999999",
            "password": "SenhaSegura123",
            "password_confirmation": "SenhaSegura123",
        },
        "terms_accepted": True,
    }


async def test_cors_allows_configured_origin_and_rejects_untrusted_refresh_origin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://app.example.com")
    application = create_app()

    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        preflight = await client.options(
            "/api/v1/auth/refresh",
            headers={
                "Origin": "https://app.example.com",
                "Access-Control-Request-Method": "POST",
            },
        )
        rejected = await client.post(
            "/api/v1/auth/refresh", headers={"Origin": "https://evil.example.com"}
        )
        allowed_without_cookie = await client.post(
            "/api/v1/auth/refresh", headers={"Origin": "https://app.example.com"}
        )

    assert preflight.status_code == 200
    assert preflight.headers["access-control-allow-origin"] == "https://app.example.com"
    assert preflight.headers["access-control-allow-credentials"] == "true"
    assert rejected.status_code == 403
    assert rejected.json()["error"]["code"] == "AUTH_PERMISSION_DENIED"
    assert allowed_without_cookie.status_code == 401
    assert (
        allowed_without_cookie.headers["access-control-allow-origin"] == "https://app.example.com"
    )


async def test_registration_verification_login_authorization_refresh_and_logout() -> None:
    repository = InMemoryRegistrationRepository()
    unit_of_work = InMemoryUnitOfWork(repository)
    passwords = FakePasswordHasher()
    tokens = HmacTokenService("integration-secret-with-at-least-32-characters")
    ids, clock, sender = SequentialIdGenerator(), FixedClock(), InMemoryEmailSender()
    app = create_app()

    async def register_dependency() -> RegisterChurch:
        return RegisterChurch(repository, unit_of_work, passwords, ids, clock, tokens, sender)

    async def verify_dependency() -> VerifyEmail:
        return VerifyEmail(repository, unit_of_work, tokens, clock)

    async def authenticate_dependency() -> AuthenticateUser:
        return AuthenticateUser(repository, unit_of_work, passwords, tokens, ids, clock)

    async def refresh_dependency() -> RefreshSession:
        return RefreshSession(repository, unit_of_work, tokens, clock)

    async def resolve_dependency() -> ResolveAccessToken:
        return ResolveAccessToken(repository, unit_of_work, tokens, clock)

    async def current_dependency() -> GetCurrentUser:
        return GetCurrentUser(repository, unit_of_work)

    async def logout_dependency() -> LogoutSession:
        return LogoutSession(repository, unit_of_work, clock)

    async def permission_dependency() -> RequirePermission:
        return RequirePermission(repository, unit_of_work, clock)

    async def logout_all_dependency() -> LogoutAllSessions:
        return LogoutAllSessions(repository, unit_of_work, clock)

    async def list_sessions_dependency() -> ListUserSessions:
        return ListUserSessions(repository, unit_of_work, clock)

    async def revoke_session_dependency() -> RevokeUserSession:
        return RevokeUserSession(repository, unit_of_work, clock)

    app.dependency_overrides.update(
        {
            get_register_church: register_dependency,
            get_verify_email: verify_dependency,
            get_authenticate: authenticate_dependency,
            get_refresh_session: refresh_dependency,
            get_resolve_access: resolve_dependency,
            get_current_user: current_dependency,
            get_logout_session: logout_dependency,
            get_require_permission: permission_dependency,
            get_logout_all_sessions: logout_all_dependency,
            get_list_sessions: list_sessions_dependency,
            get_revoke_session: revoke_session_dependency,
        }
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        registered = await client.post("/api/v1/churches", json=registration_payload())
        church_id = registered.json()["data"]["church_id"]
        blocked = await client.post(
            "/api/v1/auth/login", json={"email": "joao@igreja.com.br", "password": "SenhaSegura123"}
        )
        verified = await client.post(
            "/api/v1/auth/verify-email", json={"token": sender.verifications[0][1]}
        )
        login = await client.post(
            "/api/v1/auth/login", json={"email": "joao@igreja.com.br", "password": "SenhaSegura123"}
        )
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        me = await client.get("/api/v1/auth/me", headers=headers)
        tenant = await client.get(f"/api/v1/churches/{church_id}/me", headers=headers)
        foreign_tenant = await client.get(
            "/api/v1/churches/00000000-0000-0000-0000-000000000999/me", headers=headers
        )
        refreshed = await client.post("/api/v1/auth/refresh")
        logout_headers = {"Authorization": f"Bearer {refreshed.json()['access_token']}"}
        sessions = await client.get("/api/v1/auth/sessions", headers=logout_headers)
        logged_out = await client.post("/api/v1/auth/logout-all", headers=logout_headers)
        after_logout = await client.get("/api/v1/auth/me", headers=logout_headers)

    assert registered.status_code == 201
    assert blocked.status_code == 403
    assert blocked.json()["error"]["code"] == "AUTH_EMAIL_NOT_VERIFIED"
    assert verified.status_code == 204
    assert login.status_code == 200
    assert me.status_code == 200 and me.json()["churches"][0]["role"] == "church_owner"
    assert tenant.status_code == 200
    assert foreign_tenant.status_code == 403
    assert refreshed.status_code == 200
    assert sessions.status_code == 200 and len(sessions.json()) == 1
    assert logged_out.status_code == 204
    assert after_logout.status_code == 401
