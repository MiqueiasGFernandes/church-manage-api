import os
from collections.abc import AsyncGenerator
from typing import TypedDict

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.container import Container
from app.main import app
from modules.organizations.application.use_cases.register_church import RegisterChurch


class AddressPayload(TypedDict):
    postal_code: str
    street: str
    number: str
    complement: str | None
    district: str
    city: str
    state: str
    country: str


class AdministratorPayload(TypedDict):
    name: str
    email: str
    phone: str
    password: str
    password_confirmation: str


class ChurchRegistrationPayload(TypedDict):
    official_name: str
    display_name: str
    document: str | None
    institutional_email: str
    institutional_phone: str
    website: str | None
    slug: str
    timezone: str
    address: AddressPayload
    administrator: AdministratorPayload
    terms_accepted: bool


class InvalidChurchRegistrationPayload(ChurchRegistrationPayload):
    is_platform_admin: bool


@pytest.fixture(scope="module", autouse=True)
async def clean_postgresql_registration_tables() -> AsyncGenerator[None]:
    if os.getenv("PERSISTENCE_BACKEND") != "postgresql":
        yield
        return

    database_url = os.environ["DATABASE_URL"]
    engine = create_async_engine(database_url)

    async def truncate_tables() -> None:
        async with engine.begin() as connection:
            await connection.execute(
                text(
                    "TRUNCATE TABLE church_memberships, congregations, addresses, "
                    "church_settings, users, churches CASCADE"
                )
            )

    await truncate_tables()
    yield
    await truncate_tables()
    await engine.dispose()


def payload() -> ChurchRegistrationPayload:
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
            "password": "Senha123",
            "password_confirmation": "Senha123",
        },
        "terms_accepted": True,
    }


def test_container_resolves_typed_register_church_use_case() -> None:
    container = Container()

    use_case = container.register_church()

    assert isinstance(use_case, RegisterChurch)


async def test_returns_201_without_exposing_password_hash() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/churches", json=payload())

    assert response.status_code == 201
    body = response.json()
    assert body["data"]["status"] == "pending_email_verification"
    assert "password" not in response.text


async def test_returns_422_for_unknown_field() -> None:
    request_payload: InvalidChurchRegistrationPayload = {
        **payload(),
        "is_platform_admin": True,
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/churches", json=request_payload)

    assert response.status_code == 422
