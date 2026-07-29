from typing import TypedDict
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from modules.organizations.infrastructure.persistence.models import (
    SecurityAuditEventModel,
    SessionModel,
)
from modules.organizations.infrastructure.security import InMemoryEmailSender

pytestmark = pytest.mark.asyncio(loop_scope="session")


class AuthenticatedSession(TypedDict):
    access_token: str
    refresh_token: str


def registration_payload() -> dict[str, object]:
    return {
        "official_name": "Igreja E2E de Autenticação",
        "display_name": "Igreja E2E",
        "document": "11.222.333/0001-81",
        "institutional_email": "contato-auth-e2e@igreja.com.br",
        "institutional_phone": "+5511999999999",
        "website": None,
        "slug": "igreja-auth-e2e",
        "timezone": "America/Sao_Paulo",
        "address": {
            "postal_code": "13200-000",
            "street": "Rua dos Testes",
            "number": "100",
            "complement": None,
            "district": "Centro",
            "city": "Jundiaí",
            "state": "SP",
            "country": "BR",
        },
        "administrator": {
            "name": "Administrador E2E",
            "email": "admin-auth-e2e@igreja.com.br",
            "phone": "+5511988888888",
            "password": "SenhaSegura123",
            "password_confirmation": "SenhaSegura123",
        },
        "terms_accepted": True,
    }


async def register_verify_and_login(
    api_client: AsyncClient,
    email_sender: InMemoryEmailSender,
) -> AuthenticatedSession:
    registration = await api_client.post("/api/v1/churches", json=registration_payload())
    assert registration.status_code == 201

    verification = await api_client.post(
        "/api/v1/auth/verify-email",
        json={"token": email_sender.verifications[-1][1]},
    )
    assert verification.status_code == 204

    login = await api_client.post(
        "/api/v1/auth/login",
        json={"email": "admin-auth-e2e@igreja.com.br", "password": "SenhaSegura123"},
    )
    assert login.status_code == 200
    refresh_token = api_client.cookies.get("refresh_token")
    assert refresh_token is not None
    return {
        "access_token": str(login.json()["access_token"]),
        "refresh_token": refresh_token,
    }


def bearer(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


async def test_logout_revokes_current_session_removes_cookie_and_records_audit(
    api_client: AsyncClient,
    postgres_engine: AsyncEngine,
    email_sender: InMemoryEmailSender,
) -> None:
    authenticated = await register_verify_and_login(api_client, email_sender)

    logout = await api_client.post(
        "/api/v1/auth/logout", headers=bearer(authenticated["access_token"])
    )
    after_logout = await api_client.get(
        "/api/v1/auth/me", headers=bearer(authenticated["access_token"])
    )

    assert logout.status_code == 204
    assert api_client.cookies.get("refresh_token") is None
    assert after_logout.status_code == 401
    assert after_logout.json()["error"]["code"] == "AUTH_ACCESS_TOKEN_INVALID"

    async with AsyncSession(postgres_engine) as session:
        persisted_session = await session.scalar(select(SessionModel))
        audit_event = await session.scalar(
            select(SecurityAuditEventModel).where(
                SecurityAuditEventModel.event_type == "SESSION_REVOKED"
            )
        )

    assert persisted_session is not None
    assert persisted_session.revoked_at is not None
    assert audit_event is not None
    assert audit_event.session_id == persisted_session.id


async def test_reusing_rotated_refresh_token_revokes_persisted_session(
    api_client: AsyncClient,
    postgres_engine: AsyncEngine,
    email_sender: InMemoryEmailSender,
) -> None:
    authenticated = await register_verify_and_login(api_client, email_sender)

    refreshed = await api_client.post("/api/v1/auth/refresh")
    assert refreshed.status_code == 200
    refreshed_access_token = str(refreshed.json()["access_token"])
    assert api_client.cookies.get("refresh_token") != authenticated["refresh_token"]

    reused = await api_client.post(
        "/api/v1/auth/refresh",
        headers={"Cookie": f"refresh_token={authenticated['refresh_token']}"},
    )
    after_reuse = await api_client.get("/api/v1/auth/me", headers=bearer(refreshed_access_token))

    assert reused.status_code == 401
    assert reused.json()["error"]["code"] == "AUTH_SESSION_REVOKED"
    assert after_reuse.status_code == 401

    async with AsyncSession(postgres_engine) as session:
        persisted_session = await session.scalar(select(SessionModel))
        audit_event = await session.scalar(
            select(SecurityAuditEventModel).where(
                SecurityAuditEventModel.event_type == "SUSPICIOUS_REFRESH_TOKEN_REUSE"
            )
        )

    assert persisted_session is not None
    assert persisted_session.revoked_at is not None
    assert audit_event is not None
    assert audit_event.session_id == persisted_session.id


async def test_user_lists_and_revokes_only_an_owned_session(
    api_client: AsyncClient,
    email_sender: InMemoryEmailSender,
) -> None:
    first = await register_verify_and_login(api_client, email_sender)
    second_login = await api_client.post(
        "/api/v1/auth/login",
        json={"email": "admin-auth-e2e@igreja.com.br", "password": "SenhaSegura123"},
    )
    assert second_login.status_code == 200
    second_access_token = str(second_login.json()["access_token"])

    sessions = await api_client.get("/api/v1/auth/sessions", headers=bearer(first["access_token"]))
    assert sessions.status_code == 200
    session_items = sessions.json()
    assert len(session_items) == 2
    assert sum(item["current"] for item in session_items) == 1
    other_session_id = next(item["session_id"] for item in session_items if not item["current"])

    revoked = await api_client.delete(
        f"/api/v1/auth/sessions/{other_session_id}",
        headers=bearer(first["access_token"]),
    )
    revoked_access = await api_client.get("/api/v1/auth/me", headers=bearer(second_access_token))
    foreign_revoke = await api_client.delete(
        f"/api/v1/auth/sessions/{UUID(int=999)}",
        headers=bearer(first["access_token"]),
    )

    assert revoked.status_code == 204
    assert revoked_access.status_code == 401
    assert foreign_revoke.status_code == 404
    assert foreign_revoke.json()["error"]["code"] == "AUTH_SESSION_NOT_FOUND"
