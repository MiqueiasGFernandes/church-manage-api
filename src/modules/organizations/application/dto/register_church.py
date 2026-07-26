from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RegisterAddressInput:
    postal_code: str
    street: str
    number: str
    complement: str | None
    district: str
    city: str
    state: str
    country: str


@dataclass(frozen=True, slots=True)
class RegisterAdministratorInput:
    name: str
    email: str
    phone: str
    password: str
    password_confirmation: str


@dataclass(frozen=True, slots=True)
class RegisterChurchInput:
    official_name: str
    display_name: str
    document: str | None
    institutional_email: str
    institutional_phone: str
    website: str | None
    slug: str
    timezone: str
    address: RegisterAddressInput
    administrator: RegisterAdministratorInput
    terms_accepted: bool


@dataclass(frozen=True, slots=True)
class RegisterChurchOutput:
    church_id: UUID
    congregation_id: UUID
    administrator_id: UUID
    church_status: str
    email_verification_required: bool
