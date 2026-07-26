from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class DomainError(Exception):
    """Base class for organization-domain validation failures."""


class InvalidFieldError(DomainError):
    def __init__(self, field_name: str, message: str) -> None:
        self.field_name = field_name
        super().__init__(message)


def _required(value: str, field_name: str) -> str:
    normalized = " ".join(value.split())
    if not normalized:
        raise InvalidFieldError(field_name, "Campo obrigatório.")
    return normalized


@dataclass(frozen=True, slots=True)
class ChurchId:
    value: UUID


@dataclass(frozen=True, slots=True)
class CongregationId:
    value: UUID


@dataclass(frozen=True, slots=True)
class UserId:
    value: UUID


@dataclass(frozen=True, slots=True)
class MembershipId:
    value: UUID


@dataclass(frozen=True, slots=True)
class ChurchName:
    value: str

    def __post_init__(self) -> None:
        normalized = _required(self.value, "official_name")
        if not 3 <= len(normalized) <= 150:
            raise InvalidFieldError("official_name", "Deve possuir entre 3 e 150 caracteres.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class ChurchDisplayName:
    value: str

    def __post_init__(self) -> None:
        normalized = _required(self.value, "display_name")
        if not 2 <= len(normalized) <= 100:
            raise InvalidFieldError("display_name", "Deve possuir entre 2 e 100 caracteres.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class EmailAddress:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized) or len(normalized) > 254:
            raise InvalidFieldError("email", "Informe um e-mail válido.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class PhoneNumber:
    value: str

    def __post_init__(self) -> None:
        raw = self.value.strip()
        digits = re.sub(r"\D", "", raw)
        normalized = f"+{digits}"
        if not re.fullmatch(r"\+[1-9]\d{7,14}", normalized):
            raise InvalidFieldError("phone", "Informe um telefone com código do país.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class ChurchSlug:
    value: str
    RESERVED = frozenset(
        {
            "admin",
            "api",
            "app",
            "auth",
            "login",
            "logout",
            "cadastro",
            "configuracoes",
            "suporte",
            "sistema",
            "publico",
        }
    )

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not 3 <= len(normalized) <= 60 or not re.fullmatch(
            r"[a-z0-9]+(?:-[a-z0-9]+)*", normalized
        ):
            raise InvalidFieldError("slug", "O slug informado possui formato inválido.")
        if normalized in self.RESERVED:
            raise InvalidFieldError("slug", "O slug informado é reservado.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class CNPJ:
    value: str

    def __post_init__(self) -> None:
        digits = re.sub(r"\D", "", self.value)
        if len(digits) != 14 or digits == digits[0] * 14 or not self._valid_check_digits(digits):
            raise InvalidFieldError("document", "Informe um CNPJ válido.")
        object.__setattr__(self, "value", digits)

    @staticmethod
    def _valid_check_digits(digits: str) -> bool:
        def digit(base: str, weights: tuple[int, ...]) -> str:
            remainder = (
                sum(int(number) * weight for number, weight in zip(base, weights, strict=True)) % 11
            )
            return "0" if remainder < 2 else str(11 - remainder)

        first = digit(digits[:12], (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2))
        second = digit(digits[:12] + first, (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2))
        return digits[-2:] == first + second


@dataclass(frozen=True, slots=True)
class TimeZone:
    value: str

    def __post_init__(self) -> None:
        try:
            ZoneInfo(self.value)
        except ZoneInfoNotFoundError as exc:
            raise InvalidFieldError("timezone", "Informe um fuso horário válido.") from exc


@dataclass(frozen=True, slots=True)
class Address:
    postal_code: str
    street: str
    number: str
    complement: str | None
    district: str
    city: str
    state: str
    country: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "postal_code", _required(self.postal_code, "postal_code"))
        object.__setattr__(self, "street", _required(self.street, "street"))
        object.__setattr__(self, "number", _required(self.number, "number"))
        object.__setattr__(self, "district", _required(self.district, "district"))
        object.__setattr__(self, "city", _required(self.city, "city"))
        object.__setattr__(self, "state", _required(self.state, "state"))
        object.__setattr__(self, "country", _required(self.country, "country"))


class ChurchStatus(str, Enum):
    PENDING_EMAIL_VERIFICATION = "pending_email_verification"


class UserStatus(str, Enum):
    PENDING_EMAIL_VERIFICATION = "pending_email_verification"


class ChurchRole(str, Enum):
    CHURCH_ADMIN = "church_admin"


@dataclass(slots=True)
class Church:
    id: ChurchId
    official_name: ChurchName
    display_name: ChurchDisplayName
    document: CNPJ | None
    institutional_email: EmailAddress
    institutional_phone: PhoneNumber
    website: str | None
    slug: ChurchSlug
    timezone: TimeZone
    status: ChurchStatus
    created_at: datetime


@dataclass(frozen=True, slots=True)
class User:
    id: UserId
    name: str
    email: EmailAddress
    phone: PhoneNumber
    password_hash: str
    status: UserStatus
    created_at: datetime


@dataclass(frozen=True, slots=True)
class Congregation:
    id: CongregationId
    church_id: ChurchId
    name: str
    address: Address
    created_at: datetime


@dataclass(frozen=True, slots=True)
class ChurchMembership:
    id: MembershipId
    church_id: ChurchId
    user_id: UserId
    role: ChurchRole
    joined_at: datetime


@dataclass(frozen=True, slots=True)
class ChurchSettings:
    church_id: ChurchId
    locale: str
    currency: str
    timezone: TimeZone
    date_format: str
    country: str
