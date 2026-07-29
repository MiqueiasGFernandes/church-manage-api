from datetime import timedelta

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
from modules.organizations.application.ports.auth import IEmailSender, ITokenService
from modules.organizations.application.ports.registration_services import (
    IClock,
    IIdGenerator,
    IPasswordHasher,
    IUnitOfWork,
)
from modules.organizations.application.repositories.auth_repository import SecurityAuditEvent
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
from modules.organizations.domain.use_cases.register_church import IRegisterChurch


class RegisterChurch(IRegisterChurch):
    def __init__(
        self,
        repository: IRegistrationRepository,
        unit_of_work: IUnitOfWork,
        password_hasher: IPasswordHasher,
        id_generator: IIdGenerator,
        clock: IClock,
        token_service: ITokenService,
        email_sender: IEmailSender,
    ) -> None:
        self._repository = repository
        self._unit_of_work = unit_of_work
        self._password_hasher = password_hasher
        self._id_generator = id_generator
        self._clock = clock
        self._token_service = token_service
        self._email_sender = email_sender

    async def execute(self, data: RegisterChurchInput) -> RegisterChurchOutput:
        self._validate_registration(data)
        administrator_email = EmailAddress(data.administrator.email)
        slug = ChurchSlug(data.slug)
        document = CNPJ(data.document) if data.document else None
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
            ChurchRole.CHURCH_OWNER,
            now,
        )
        settings = ChurchSettings(church_id, "pt-BR", "BRL", timezone, "DD/MM/YYYY", "BR")

        async with self._unit_of_work:
            if await self._repository.user_exists_by_email(administrator_email):
                raise UserEmailAlreadyExistsError("Já existe uma conta cadastrada com este e-mail.")
            if await self._repository.church_exists_by_slug(slug):
                raise ChurchSlugAlreadyExistsError("O endereço público escolhido já está em uso.")
            if document is not None and await self._repository.church_exists_by_document(document):
                raise ChurchDocumentAlreadyExistsError(
                    "Já existe uma igreja cadastrada com este CNPJ."
                )
            await self._repository.add_church(church)
            await self._repository.add_user(user)
            await self._repository.add_congregation(congregation)
            await self._repository.add_membership(membership)
            await self._repository.add_settings(settings)
            verification_token = self._token_service.generate_opaque()
            await self._repository.add_email_verification(
                user_id.value,
                self._token_service.hash_opaque(verification_token),
                now + timedelta(hours=24),
            )
            await self._repository.add_audit_event(
                SecurityAuditEvent(
                    "USER_REGISTERED",
                    now,
                    actor_user_id=user_id.value,
                    target_user_id=user_id.value,
                    church_id=church_id.value,
                )
            )
            await self._repository.add_audit_event(
                SecurityAuditEvent(
                    "EMAIL_VERIFICATION_REQUESTED",
                    now,
                    actor_user_id=user_id.value,
                    target_user_id=user_id.value,
                    church_id=church_id.value,
                )
            )
            await self._unit_of_work.commit()
        await self._email_sender.send_email_verification(
            administrator_email.value, verification_token
        )
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
        if len(password) < 10 or password.casefold() == data.administrator.email.strip().casefold():
            raise WeakPasswordError(
                "A senha deve ter ao menos 10 caracteres e não pode ser igual ao e-mail."
            )
        if not " ".join(data.administrator.name.split()):
            raise RegistrationError("O nome do administrador é obrigatório.")
