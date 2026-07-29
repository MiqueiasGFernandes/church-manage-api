from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from modules.organizations.application.dto.register_church import (
    RegisterAddressInput,
    RegisterAdministratorInput,
    RegisterChurchInput,
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
from modules.organizations.application.ports.auth import IRateLimiter, RateLimitAction
from modules.organizations.domain.model import DomainError, InvalidFieldError
from modules.organizations.domain.use_cases.register_church import IRegisterChurch
from modules.organizations.presentation.auth_http import client_address, get_rate_limiter

router = APIRouter(prefix="/api/v1/churches", tags=["churches"])


class AddressRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    postal_code: str = Field(max_length=16)
    street: str = Field(max_length=200)
    number: str = Field(max_length=30)
    complement: str | None = Field(default=None, max_length=100)
    district: str = Field(max_length=100)
    city: str = Field(max_length=100)
    state: str = Field(max_length=50)
    country: str = Field(max_length=2)


class AdministratorRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(max_length=150)
    email: str = Field(max_length=254)
    phone: str = Field(max_length=32)
    password: str = Field(min_length=10, max_length=128)
    password_confirmation: str = Field(min_length=10, max_length=128)


class RegisterChurchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    official_name: str = Field(max_length=150)
    display_name: str = Field(max_length=100)
    document: str | None = Field(default=None, max_length=18)
    institutional_email: str = Field(max_length=254)
    institutional_phone: str = Field(max_length=32)
    website: str | None = Field(default=None, max_length=2048)
    slug: str = Field(max_length=60)
    timezone: str = Field(max_length=64)
    address: AddressRequest
    administrator: AdministratorRequest
    terms_accepted: bool


class RegisterChurchData(BaseModel):
    church_id: UUID
    congregation_id: UUID
    administrator_id: UUID
    status: str
    email_verification_required: bool


class RegisterChurchResponse(BaseModel):
    data: RegisterChurchData


async def get_register_church() -> IRegisterChurch:
    raise RuntimeError("A dependência deve ser configurada pelo composition root.")


@router.post("", response_model=RegisterChurchResponse, status_code=status.HTTP_201_CREATED)
async def register_church(
    body: RegisterChurchRequest,
    request: Request,
    use_case: IRegisterChurch = Depends(get_register_church),
    rate_limiter: IRateLimiter = Depends(get_rate_limiter),
) -> RegisterChurchResponse:
    await rate_limiter.ensure_allowed(
        RateLimitAction.REGISTER_CHURCH,
        f"register-church:{client_address(request)}:{body.administrator.email.strip().casefold()}",
    )
    address = RegisterAddressInput(
        postal_code=body.address.postal_code,
        street=body.address.street,
        number=body.address.number,
        complement=body.address.complement,
        district=body.address.district,
        city=body.address.city,
        state=body.address.state,
        country=body.address.country,
    )
    administrator = RegisterAdministratorInput(
        name=body.administrator.name,
        email=body.administrator.email,
        phone=body.administrator.phone,
        password=body.administrator.password,
        password_confirmation=body.administrator.password_confirmation,
    )
    result = await use_case.execute(
        RegisterChurchInput(
            official_name=body.official_name,
            display_name=body.display_name,
            document=body.document,
            institutional_email=body.institutional_email,
            institutional_phone=body.institutional_phone,
            website=body.website,
            slug=body.slug,
            timezone=body.timezone,
            address=address,
            administrator=administrator,
            terms_accepted=body.terms_accepted,
        )
    )
    return RegisterChurchResponse(
        data=RegisterChurchData(
            church_id=result.church_id,
            congregation_id=result.congregation_id,
            administrator_id=result.administrator_id,
            status=result.church_status,
            email_verification_required=result.email_verification_required,
        )
    )


async def registration_error_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, InvalidFieldError):
        request.state.error_code = "VALIDATION_ERROR"
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(exc),
                    "fields": {exc.field_name: [str(exc)]},
                }
            },
        )
    conflict_types = (
        UserEmailAlreadyExistsError,
        ChurchSlugAlreadyExistsError,
        ChurchDocumentAlreadyExistsError,
    )
    if isinstance(exc, conflict_types):
        request.state.error_code = exc.code
        return JSONResponse(
            status_code=409, content={"error": {"code": exc.code, "message": str(exc)}}
        )
    code = exc.code if isinstance(exc, RegistrationError) else "VALIDATION_ERROR"
    request.state.error_code = code
    return JSONResponse(status_code=422, content={"error": {"code": code, "message": str(exc)}})


HANDLED_ERRORS = (
    DomainError,
    RegistrationError,
    TermsNotAcceptedError,
    PasswordMismatchError,
    WeakPasswordError,
)
