from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.organizations.application.repositories.registration_repository import (
    IRegistrationRepository,
)
from modules.organizations.domain.model import (
    CNPJ,
    Church,
    ChurchMembership,
    ChurchSettings,
    ChurchSlug,
    Congregation,
    EmailAddress,
    User,
)
from modules.organizations.infrastructure.persistence.mappers import RegistrationMapper
from modules.organizations.infrastructure.persistence.models import ChurchModel, UserModel


class SqlAlchemyRegistrationRepository(IRegistrationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def user_exists_by_email(self, email: EmailAddress) -> bool:
        statement = select(exists().where(UserModel.email == email.value))
        return bool(await self._session.scalar(statement))

    async def church_exists_by_slug(self, slug: ChurchSlug) -> bool:
        statement = select(exists().where(ChurchModel.slug == slug.value))
        return bool(await self._session.scalar(statement))

    async def church_exists_by_document(self, document: CNPJ) -> bool:
        statement = select(exists().where(ChurchModel.document == document.value))
        return bool(await self._session.scalar(statement))

    async def add_church(self, church: Church) -> None:
        self._session.add(RegistrationMapper.church_to_model(church))

    async def add_user(self, user: User) -> None:
        self._session.add(RegistrationMapper.user_to_model(user))

    async def add_congregation(self, congregation: Congregation) -> None:
        await self._session.flush()
        address_model, congregation_model = RegistrationMapper.congregation_to_models(congregation)
        self._session.add_all((address_model, congregation_model))

    async def add_membership(self, membership: ChurchMembership) -> None:
        self._session.add(RegistrationMapper.membership_to_model(membership))

    async def add_settings(self, settings: ChurchSettings) -> None:
        self._session.add(RegistrationMapper.settings_to_model(settings))
