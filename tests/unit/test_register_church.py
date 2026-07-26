import unittest
from dataclasses import replace
from datetime import datetime, timezone
from uuid import UUID

from modules.organizations.application.dto.register_church import (
    RegisterAddressInput,
    RegisterAdministratorInput,
    RegisterChurchInput,
)
from modules.organizations.application.errors.register_church import (
    ChurchSlugAlreadyExistsError,
    PasswordMismatchError,
    TermsNotAcceptedError,
    UserEmailAlreadyExistsError,
)
from modules.organizations.application.use_cases.register_church import RegisterChurch
from modules.organizations.infrastructure.in_memory import (
    InMemoryEventPublisher,
    InMemoryRegistrationRepository,
    InMemoryUnitOfWork,
)


class FakeHasher:
    def hash(self, plain_text: str) -> str:
        return f"hashed:{len(plain_text)}"


class SequentialIdGenerator:
    def __init__(self) -> None:
        self._value = 0

    def generate(self) -> UUID:
        self._value += 1
        return UUID(int=self._value)


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 7, 25, tzinfo=timezone.utc)


def valid_input() -> RegisterChurchInput:
    return RegisterChurchInput(
        official_name="Igreja Batista Central de Jundiaí",
        display_name="Igreja Batista Central",
        document="11.222.333/0001-81",
        institutional_email="CONTATO@IGREJA.COM.BR",
        institutional_phone="+5511999999999",
        website="https://igreja.com.br",
        slug="igreja-central-jundiai",
        timezone="America/Sao_Paulo",
        address=RegisterAddressInput(
            postal_code="13200-000",
            street="Rua das Igrejas",
            number="100",
            complement=None,
            district="Centro",
            city="Jundiaí",
            state="SP",
            country="BR",
        ),
        administrator=RegisterAdministratorInput(
            name="João da Silva",
            email="JOAO@IGREJA.COM.BR",
            phone="+5511999999999",
            password="Senha123",
            password_confirmation="Senha123",
        ),
        terms_accepted=True,
    )


class RegisterChurchTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.repository = InMemoryRegistrationRepository()
        self.publisher = InMemoryEventPublisher()
        self.use_case = RegisterChurch(
            repository=self.repository,
            unit_of_work=InMemoryUnitOfWork(self.repository),
            password_hasher=FakeHasher(),
            id_generator=SequentialIdGenerator(),
            clock=FixedClock(),
            event_publisher=self.publisher,
        )

    async def test_registers_complete_church_atomically(self) -> None:
        result = await self.use_case.execute(valid_input())

        self.assertEqual(result.church_status, "pending_email_verification")
        self.assertTrue(result.email_verification_required)
        self.assertEqual(len(self.repository.churches), 1)
        self.assertEqual(len(self.repository.congregations), 1)
        self.assertEqual(self.repository.congregations[0].name, "Sede")
        self.assertEqual(len(self.repository.users), 1)
        self.assertNotIn("Senha123", self.repository.users[0].password_hash)
        self.assertEqual(self.repository.memberships[0].role.value, "church_admin")
        self.assertEqual(self.repository.settings[0].locale, "pt-BR")
        self.assertEqual(len(self.publisher.events), 1)

    async def test_rejects_existing_administrator_email_without_side_effects(self) -> None:
        await self.use_case.execute(valid_input())
        with self.assertRaises(UserEmailAlreadyExistsError):
            await self.use_case.execute(valid_input())
        self.assertEqual(len(self.repository.churches), 1)

    async def test_rejects_existing_slug(self) -> None:
        await self.use_case.execute(valid_input())
        changed = valid_input()
        changed = replace(
            changed,
            administrator=RegisterAdministratorInput(
                name="Maria Silva",
                email="maria@igreja.com.br",
                phone="+5511988888888",
                password="Senha123",
                password_confirmation="Senha123",
            ),
        )
        with self.assertRaises(ChurchSlugAlreadyExistsError):
            await self.use_case.execute(changed)

    async def test_rejects_terms_and_password_mismatch(self) -> None:
        original = valid_input()
        without_terms = RegisterChurchInput(
            official_name=original.official_name,
            display_name=original.display_name,
            document=original.document,
            institutional_email=original.institutional_email,
            institutional_phone=original.institutional_phone,
            website=original.website,
            slug=original.slug,
            timezone=original.timezone,
            address=original.address,
            administrator=original.administrator,
            terms_accepted=False,
        )
        with self.assertRaises(TermsNotAcceptedError):
            await self.use_case.execute(without_terms)

        mismatched_admin = RegisterAdministratorInput(
            name=original.administrator.name,
            email=original.administrator.email,
            phone=original.administrator.phone,
            password="Senha123",
            password_confirmation="Outra123",
        )
        mismatch = RegisterChurchInput(
            official_name=original.official_name,
            display_name=original.display_name,
            document=original.document,
            institutional_email=original.institutional_email,
            institutional_phone=original.institutional_phone,
            website=original.website,
            slug=original.slug,
            timezone=original.timezone,
            address=original.address,
            administrator=mismatched_admin,
            terms_accepted=True,
        )
        with self.assertRaises(PasswordMismatchError):
            await self.use_case.execute(mismatch)


if __name__ == "__main__":
    unittest.main()
