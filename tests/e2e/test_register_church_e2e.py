from copy import deepcopy
from typing import Literal, TypedDict
from uuid import UUID

import pytest
from httpx import AsyncClient
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from modules.organizations.infrastructure.persistence.models import (
    AddressModel,
    ChurchMembershipModel,
    ChurchModel,
    ChurchSettingsModel,
    CongregationModel,
    UserModel,
)
from modules.organizations.infrastructure.security import InMemoryEmailSender

pytestmark = pytest.mark.asyncio(loop_scope="session")


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


class RegistrationData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    church_id: UUID
    congregation_id: UUID
    administrator_id: UUID
    status: Literal["pending_email_verification"]
    email_verification_required: Literal[True]


class RegistrationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data: RegistrationData


class RegistrationError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    fields: dict[str, list[str]] | None = None


class RegistrationErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: RegistrationError


def church_payload() -> ChurchRegistrationPayload:
    return {
        "official_name": "Igreja Batista Central de Jundiaí",
        "display_name": "Igreja Batista Central",
        "document": "11.222.333/0001-81",
        "institutional_email": "CONTATO@IGREJA.COM.BR",
        "institutional_phone": "+55 (11) 99999-9999",
        "website": "https://igreja.com.br",
        "slug": "Igreja-Central-Jundiai",
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
            "email": "JOAO@IGREJA.COM.BR",
            "phone": "+55 (11) 98888-8888",
            "password": "SenhaSegura123",
            "password_confirmation": "SenhaSegura123",
        },
        "terms_accepted": True,
    }


async def registration_counts(engine: AsyncEngine) -> tuple[int, int, int, int, int, int]:
    async with AsyncSession(engine) as session:
        churches = await session.scalar(select(func.count()).select_from(ChurchModel))
        users = await session.scalar(select(func.count()).select_from(UserModel))
        addresses = await session.scalar(select(func.count()).select_from(AddressModel))
        congregations = await session.scalar(select(func.count()).select_from(CongregationModel))
        memberships = await session.scalar(select(func.count()).select_from(ChurchMembershipModel))
        settings = await session.scalar(select(func.count()).select_from(ChurchSettingsModel))
    assert churches is not None
    assert users is not None
    assert addresses is not None
    assert congregations is not None
    assert memberships is not None
    assert settings is not None
    return churches, users, addresses, congregations, memberships, settings


async def test_registers_complete_church_through_http(
    api_client: AsyncClient,
    postgres_engine: AsyncEngine,
    email_sender: InMemoryEmailSender,
) -> None:
    response = await api_client.post("/api/v1/churches", json=church_payload())

    assert response.status_code == 201
    result = RegistrationResponse.model_validate_json(response.text).data
    assert result.status == "pending_email_verification"
    assert result.email_verification_required is True
    assert "password" not in response.text.lower()

    pending_login = await api_client.post(
        "/api/v1/auth/login",
        json={"email": "joao@igreja.com.br", "password": "SenhaSegura123"},
    )
    verification = await api_client.post(
        "/api/v1/auth/verify-email", json={"token": email_sender.verifications[-1][1]}
    )
    login = await api_client.post(
        "/api/v1/auth/login",
        json={"email": "joao@igreja.com.br", "password": "SenhaSegura123"},
    )
    me = await api_client.get(
        f"/api/v1/churches/{result.church_id}/me",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )

    assert pending_login.status_code == 403
    assert verification.status_code == 204
    assert login.status_code == 200
    assert me.status_code == 200
    assert me.json()["churches"][0]["role"] == "church_owner"

    reset_requested = await api_client.post(
        "/api/v1/auth/forgot-password", json={"email": "joao@igreja.com.br"}
    )
    password_reset = await api_client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": email_sender.password_resets[-1][1],
            "new_password": "NovaSenhaSegura123",
        },
    )
    new_login = await api_client.post(
        "/api/v1/auth/login",
        json={"email": "joao@igreja.com.br", "password": "NovaSenhaSegura123"},
    )

    assert reset_requested.status_code == 204
    assert password_reset.status_code == 204
    assert new_login.status_code == 200

    async with AsyncSession(postgres_engine) as session:
        church = await session.get(ChurchModel, result.church_id)
        administrator = await session.get(UserModel, result.administrator_id)
        congregation = await session.get(CongregationModel, result.congregation_id)
        membership = await session.scalar(
            select(ChurchMembershipModel).where(
                ChurchMembershipModel.church_id == result.church_id,
                ChurchMembershipModel.user_id == result.administrator_id,
            )
        )
        settings = await session.get(ChurchSettingsModel, result.church_id)

        assert church is not None
        assert church.document == "11222333000181"
        assert church.institutional_email == "contato@igreja.com.br"
        assert church.institutional_phone == "+5511999999999"
        assert church.slug == "igreja-central-jundiai"
        assert church.status == "pending_email_verification"

        assert administrator is not None
        assert administrator.email == "joao@igreja.com.br"
        assert administrator.phone == "+5511988888888"
        assert administrator.password_hash != "SenhaSegura123"
        assert administrator.password_hash.startswith("$argon2")
        assert administrator.status == "active"

        assert congregation is not None
        assert congregation.church_id == result.church_id
        assert congregation.name == "Sede"
        address = await session.get(AddressModel, congregation.address_id)
        assert address is not None
        assert address.church_id == result.church_id

        assert membership is not None
        assert membership.role == "church_owner"

        assert settings is not None
        assert settings.locale == "pt-BR"
        assert settings.currency == "BRL"
        assert settings.timezone == "America/Sao_Paulo"


@pytest.mark.parametrize(
    ("conflict", "expected_code"),
    [
        ("email", "USER_EMAIL_ALREADY_EXISTS"),
        ("slug", "CHURCH_SLUG_ALREADY_EXISTS"),
        ("document", "CHURCH_DOCUMENT_ALREADY_EXISTS"),
    ],
)
async def test_rejects_duplicate_registration_without_partial_effects(
    api_client: AsyncClient,
    postgres_engine: AsyncEngine,
    conflict: Literal["email", "slug", "document"],
    expected_code: str,
) -> None:
    original_payload = church_payload()
    duplicate_payload = deepcopy(original_payload)
    duplicate_payload["administrator"]["email"] = "maria@igreja.com.br"
    duplicate_payload["slug"] = "outra-igreja"
    duplicate_payload["document"] = None

    if conflict == "email":
        duplicate_payload["administrator"]["email"] = original_payload["administrator"]["email"]
    elif conflict == "slug":
        duplicate_payload["slug"] = original_payload["slug"]
    else:
        duplicate_payload["document"] = original_payload["document"]

    first_response = await api_client.post("/api/v1/churches", json=original_payload)
    duplicate_response = await api_client.post("/api/v1/churches", json=duplicate_payload)

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409
    error = RegistrationErrorResponse.model_validate_json(duplicate_response.text).error
    assert error.code == expected_code
    assert original_payload["administrator"]["password"] not in duplicate_response.text
    assert await registration_counts(postgres_engine) == (1, 1, 1, 1, 1, 1)


@pytest.mark.parametrize(
    ("rejection", "expected_code"),
    [
        ("terms", "TERMS_NOT_ACCEPTED"),
        ("password", "PASSWORD_MISMATCH"),
        ("email", "VALIDATION_ERROR"),
        ("document", "VALIDATION_ERROR"),
    ],
)
async def test_rejects_invalid_business_conditions_without_persisting_data(
    api_client: AsyncClient,
    postgres_engine: AsyncEngine,
    rejection: Literal["terms", "password", "email", "document"],
    expected_code: str,
) -> None:
    request_payload = church_payload()
    if rejection == "terms":
        request_payload["terms_accepted"] = False
    elif rejection == "password":
        request_payload["administrator"]["password_confirmation"] = "OutraSenha123"
    elif rejection == "email":
        request_payload["administrator"]["email"] = "email-invalido"
    else:
        request_payload["document"] = "11.111.111/1111-11"

    response = await api_client.post("/api/v1/churches", json=request_payload)

    assert response.status_code == 422
    error = RegistrationErrorResponse.model_validate_json(response.text).error
    assert error.code == expected_code
    if rejection in ("email", "document"):
        assert error.fields is not None
        assert rejection in error.fields
    assert request_payload["administrator"]["password"] not in response.text
    assert await registration_counts(postgres_engine) == (0, 0, 0, 0, 0, 0)


async def test_rejects_missing_required_field_without_persisting_data(
    api_client: AsyncClient,
    postgres_engine: AsyncEngine,
) -> None:
    request_payload: dict[str, object] = dict(church_payload())
    request_payload.pop("official_name")

    response = await api_client.post("/api/v1/churches", json=request_payload)

    assert response.status_code == 422
    assert '"official_name"' in response.text
    assert await registration_counts(postgres_engine) == (0, 0, 0, 0, 0, 0)
