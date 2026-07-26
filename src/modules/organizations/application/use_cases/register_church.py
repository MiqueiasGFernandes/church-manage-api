from modules.organizations.application.dto.register_church import (
    RegisterChurchInput,
    RegisterChurchOutput,
)
from modules.organizations.application.errors.register_church import (
    ChurchDocumentAlreadyExistsError,
    ChurchSlugAlreadyExistsError,
    PasswordMismatchError,
    RegistrationError,
    TermsNotAcceptedError,
    UserEmailAlreadyExistsError,
    WeakPasswordError,
)
from modules.organizations.application.ports.registration_services import (
    IClock,
    IEventPublisher,
    IIdGenerator,
    IPasswordHasher,
    IUnitOfWork,
)
from modules.organizations.application.repositories.registration_repository import (
    IRegistrationRepository,
)
from modules.organizations.domain.model import (
    CNPJ,
    Address,
    Church,
    ChurchDisplayName,
    ChurchId,
    ChurchMembership,
    ChurchName,
    ChurchRegistered,
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


class RegisterChurch:
    def __init__(
        self,
        repository: IRegistrationRepository,
        unit_of_work: IUnitOfWork,
        password_hasher: IPasswordHasher,
        id_generator: IIdGenerator,
        clock: IClock,
        event_publisher: IEventPublisher,
    ) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work
        self._password_hasher = password_hasher
        self._id_generator = id_generator
        self._clock = clock
        self._event_publisher = event_publisher

    async def execute(self, data: RegisterChurchInput) -> RegisterChurchOutput:
        self._validate_registration(data)
        administrator_email = EmailAddress(data.administrator.email)
        slug = ChurchSlug(data.slug)
        document = CNPJ(data.document) if data.document else None
        if await self._repository.user_exists_by_email(administrator_email):
            raise UserEmailAlreadyExistsError("Já existe uma conta cadastrada com este e-mail.")
        if await self._repository.church_exists_by_slug(slug):
            raise ChurchSlugAlreadyExistsError("O endereço público escolhido já está em uso.")
        if document is not None and await self._repository.church_exists_by_document(document):
            raise ChurchDocumentAlreadyExistsError("Já existe uma igreja cadastrada com este CNPJ.")

        now = self._clock.now()
        church_id, congregation_id, user_id = (
            ChurchId(self._id_generator.generate()),
            CongregationId(self._id_generator.generate()),
            UserId(self._id_generator.generate()),
        )
        timezone = TimeZone(data.timezone)
        church = Church(
            church_id,
            ChurchName(data.official_name),
            ChurchDisplayName(data.display_name),
            document,
            EmailAddress(data.institutional_email),
            PhoneNumber(data.institutional_phone),
            data.website,
            slug,
            timezone,
            ChurchStatus.PENDING_EMAIL_VERIFICATION,
            now,
        )
        user = User(
            user_id,
            " ".join(data.administrator.name.split()),
            administrator_email,
            PhoneNumber(data.administrator.phone),
            self._password_hasher.hash(data.administrator.password),
            UserStatus.PENDING_EMAIL_VERIFICATION,
            now,
        )
        address = Address(
            postal_code=data.address.postal_code,
            street=data.address.street,
            number=data.address.number,
            complement=data.address.complement,
            district=data.address.district,
            city=data.address.city,
            state=data.address.state,
            country=data.address.country,
        )
        congregation = Congregation(congregation_id, church_id, "Sede", address, now)
        membership = ChurchMembership(
            MembershipId(self._id_generator.generate()),
            church_id,
            user_id,
            ChurchRole.CHURCH_ADMIN,
            now,
        )
        settings = ChurchSettings(church_id, "pt-BR", "BRL", timezone, "DD/MM/YYYY", "BR")
        event = ChurchRegistered(church_id, user_id, church.institutional_email, now)
        church.events.append(event)

        async with self._unit_of_work:
            await self._repository.add_church(church)
            await self._repository.add_user(user)
            await self._repository.add_congregation(congregation)
            await self._repository.add_membership(membership)
            await self._repository.add_settings(settings)
            await self._unit_of_work.commit()
        await self._event_publisher.publish(event)
        return RegisterChurchOutput(
            church_id.value, congregation_id.value, user_id.value, church.status.value, True
        )

    @staticmethod
    def _validate_registration(data: RegisterChurchInput) -> None:
        if not data.terms_accepted:
            raise TermsNotAcceptedError("O aceite dos termos é necessário.")
        if data.administrator.password != data.administrator.password_confirmation:
            raise PasswordMismatchError("As senhas não coincidem.")
        password = data.administrator.password
        if (
            len(password) < 8
            or not any(character.isalpha() for character in password)
            or not any(character.isdigit() for character in password)
        ):
            raise WeakPasswordError(
                "A senha deve ter ao menos 8 caracteres, uma letra e um número."
            )
        if not " ".join(data.administrator.name.split()):
            raise RegistrationError("O nome do administrador é obrigatório.")
