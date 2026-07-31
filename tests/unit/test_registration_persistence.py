from collections.abc import Iterable
from datetime import UTC, datetime
from uuid import UUID

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.container import Container
from modules.organizations.application.errors.register_church import (
    ChurchDocumentAlreadyExistsError,
    ChurchSlugAlreadyExistsError,
    RegistrationError,
    UserEmailAlreadyExistsError,
)
from modules.organizations.application.use_cases.register_church import RegisterChurch
from modules.organizations.domain.model import (
    CNPJ,
    Address,
    Church,
    ChurchDisplayName,
    ChurchId,
    ChurchMembership,
    ChurchName,
    ChurchRole,
    ChurchSettings,
    ChurchSlug,
    ChurchStatus,
    Congregation,
    CongregationId,
    EmailAddress,
    MembershipId,
    PhoneNumber,
    TimeZone,
    User,
    UserId,
    UserStatus,
)
from modules.organizations.infrastructure.persistence.database import (
    PostgresDatabase,
    psycopg_url,
)
from modules.organizations.infrastructure.persistence.mappers import RegistrationMapper
from modules.organizations.infrastructure.persistence.models import (
    AddressModel,
    ChurchMembershipModel,
    ChurchModel,
    ChurchSettingsModel,
    CongregationModel,
    UserModel,
)
from modules.organizations.infrastructure.persistence.registration_repository import (
    SqlAlchemyRegistrationRepository,
)
from modules.organizations.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork


class RecordingAsyncSession(AsyncSession):
    def __init__(self) -> None:
        self.commit_calls = 0
        self.rollback_calls = 0
        self.close_calls = 0

    async def commit(self) -> None:
        self.commit_calls += 1

    async def rollback(self) -> None:
        self.rollback_calls += 1

    async def close(self) -> None:
        self.close_calls += 1


class RecordingRepositorySession(AsyncSession):
    def __init__(self) -> None:
        self.added: list[object] = []
        self.flush_calls = 0

    def add(self, instance: object, _warn: bool = True) -> None:
        self.added.append(instance)

    def add_all(self, instances: Iterable[object]) -> None:
        self.added.extend(instances)

    async def flush(self, objects: Iterable[object] | None = None) -> None:
        self.flush_calls += 1


class FailingCommitSession(RecordingAsyncSession):
    def __init__(self, constraint_name: str) -> None:
        super().__init__()
        self._constraint_name = constraint_name

    async def commit(self) -> None:
        raise IntegrityError(
            "INSERT",
            {},
            RuntimeError(f'violates unique constraint "{self._constraint_name}"'),
        )


def persistence_entities() -> tuple[Church, User, Congregation, ChurchMembership, ChurchSettings]:
    now = datetime(2026, 7, 26, tzinfo=UTC)
    church_id = ChurchId(UUID(int=1))
    user_id = UserId(UUID(int=2))
    timezone = TimeZone("America/Sao_Paulo")
    church = Church(
        id=church_id,
        official_name=ChurchName("Igreja Batista Central de Jundiaí"),
        display_name=ChurchDisplayName("Igreja Batista Central"),
        document=CNPJ("11.222.333/0001-81"),
        institutional_email=EmailAddress("contato@igreja.com.br"),
        institutional_phone=PhoneNumber("+5511999999999"),
        website="https://igreja.com.br",
        slug=ChurchSlug("igreja-central-jundiai"),
        timezone=timezone,
        status=ChurchStatus.PENDING_EMAIL_VERIFICATION,
        created_at=now,
    )
    user = User(
        id=user_id,
        name="João da Silva",
        email=EmailAddress("joao@igreja.com.br"),
        phone=PhoneNumber("+5511988888888"),
        password_hash="argon2-hash",
        status=UserStatus.PENDING_EMAIL_VERIFICATION,
        created_at=now,
    )
    congregation = Congregation(
        id=CongregationId(UUID(int=3)),
        church_id=church_id,
        name="Sede",
        address=Address(
            postal_code="13200-000",
            street="Rua das Igrejas",
            number="100",
            complement=None,
            district="Centro",
            city="Jundiaí",
            state="SP",
            country="BR",
        ),
        created_at=now,
    )
    membership = ChurchMembership(
        id=MembershipId(UUID(int=4)),
        church_id=church_id,
        user_id=user_id,
        role=ChurchRole.CHURCH_ADMIN,
        joined_at=now,
    )
    settings = ChurchSettings(
        church_id=church_id,
        locale="pt-BR",
        currency="BRL",
        timezone=timezone,
        date_format="DD/MM/YYYY",
        country="BR",
    )
    return church, user, congregation, membership, settings


def test_maps_registration_domain_to_separate_orm_models() -> None:
    church, user, congregation, membership, settings = persistence_entities()

    church_model = RegistrationMapper.church_to_model(church)
    user_model = RegistrationMapper.user_to_model(user)
    address_model, congregation_model = RegistrationMapper.congregation_to_models(congregation)
    membership_model = RegistrationMapper.membership_to_model(membership)
    settings_model = RegistrationMapper.settings_to_model(settings)

    assert church_model.id == church.id.value
    assert church_model.document == "11222333000181"
    assert user_model.email == "joao@igreja.com.br"
    assert address_model.church_id == church.id.value
    assert congregation_model.address_id == address_model.id
    assert membership_model.user_id == user.id.value
    assert settings_model.timezone == "America/Sao_Paulo"


@pytest.mark.asyncio
async def test_repository_stages_complete_registration_in_shared_session() -> None:
    church, user, congregation, membership, settings = persistence_entities()
    session = RecordingRepositorySession()
    repository = SqlAlchemyRegistrationRepository(session)

    await repository.add_church(church)
    await repository.add_user(user)
    await repository.add_congregation(congregation)
    await repository.add_membership(membership)
    await repository.add_settings(settings)

    assert [type(model) for model in session.added] == [
        ChurchModel,
        UserModel,
        AddressModel,
        CongregationModel,
        ChurchMembershipModel,
        ChurchSettingsModel,
    ]
    assert session.flush_calls == 1


@pytest.mark.asyncio
async def test_unit_of_work_commits_and_closes_shared_session() -> None:
    session = RecordingAsyncSession()
    unit_of_work = SqlAlchemyUnitOfWork(session)

    async with unit_of_work:
        await unit_of_work.commit()

    assert session.commit_calls == 1
    assert session.rollback_calls == 0
    assert session.close_calls == 1


@pytest.mark.asyncio
async def test_unit_of_work_rolls_back_when_scope_fails() -> None:
    session = RecordingAsyncSession()
    unit_of_work = SqlAlchemyUnitOfWork(session)

    with pytest.raises(RuntimeError, match="failure"):
        async with unit_of_work:
            raise RuntimeError("failure")

    assert session.commit_calls == 0
    assert session.rollback_calls == 1
    assert session.close_calls == 1


@pytest.mark.parametrize(
    ("constraint_name", "expected_error"),
    [
        ("uq_users_email", UserEmailAlreadyExistsError),
        ("uq_churches_slug", ChurchSlugAlreadyExistsError),
        ("uq_churches_document", ChurchDocumentAlreadyExistsError),
    ],
)
@pytest.mark.asyncio
async def test_unit_of_work_translates_registration_conflicts(
    constraint_name: str,
    expected_error: type[RegistrationError],
) -> None:
    session = FailingCommitSession(constraint_name)
    unit_of_work = SqlAlchemyUnitOfWork(session)

    with pytest.raises(expected_error):
        async with unit_of_work:
            await unit_of_work.commit()

    assert session.rollback_calls == 2
    assert session.close_calls == 1


def test_postgres_database_requires_connection_url() -> None:
    with pytest.raises(ValueError, match="DATABASE_URL"):
        PostgresDatabase("")


def test_postgres_database_uses_psycopg_with_native_neon_url() -> None:
    database_url = psycopg_url(
        "postgresql://user:password@ep-example-pooler.us-east-1.aws.neon.tech/db?sslmode=require"
    )

    assert database_url.drivername == "postgresql+psycopg"
    assert database_url.host == "ep-example-pooler.us-east-1.aws.neon.tech"


@pytest.mark.asyncio
async def test_container_resolves_postgresql_registration_use_case() -> None:
    container = Container()
    container.config.persistence_backend.from_value("postgresql")
    container.config.database_url.from_value(
        "postgresql+asyncpg://user:password@localhost:5432/church_manage"
    )

    use_case = container.register_church()

    assert isinstance(use_case, RegisterChurch)
    await container.database().dispose()
