import pytest
from pydantic import BaseModel, ValidationError

from modules.organizations.presentation.auth_http import (
    ChangePasswordRequest,
    EmailRequest,
    LoginRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from modules.organizations.presentation.http import (
    AddressRequest,
    AdministratorRequest,
    RegisterChurchRequest,
)


@pytest.mark.parametrize(
    ("request_model", "field_name", "maximum_length"),
    [
        (VerifyEmailRequest, "token", 128),
        (LoginRequest, "email", 254),
        (LoginRequest, "password", 128),
        (EmailRequest, "email", 254),
        (ResetPasswordRequest, "token", 128),
        (ResetPasswordRequest, "new_password", 128),
        (ChangePasswordRequest, "current_password", 128),
        (ChangePasswordRequest, "new_password", 128),
        (AddressRequest, "postal_code", 16),
        (AddressRequest, "street", 200),
        (AddressRequest, "number", 30),
        (AddressRequest, "complement", 100),
        (AddressRequest, "district", 100),
        (AddressRequest, "city", 100),
        (AddressRequest, "state", 50),
        (AddressRequest, "country", 2),
        (AdministratorRequest, "name", 150),
        (AdministratorRequest, "email", 254),
        (AdministratorRequest, "phone", 32),
        (AdministratorRequest, "password", 128),
        (AdministratorRequest, "password_confirmation", 128),
        (RegisterChurchRequest, "official_name", 150),
        (RegisterChurchRequest, "display_name", 100),
        (RegisterChurchRequest, "document", 18),
        (RegisterChurchRequest, "institutional_email", 254),
        (RegisterChurchRequest, "institutional_phone", 32),
        (RegisterChurchRequest, "website", 2048),
        (RegisterChurchRequest, "slug", 60),
        (RegisterChurchRequest, "timezone", 64),
    ],
)
def test_rejects_string_input_larger_than_its_use_specific_limit(
    request_model: type[BaseModel], field_name: str, maximum_length: int
) -> None:
    with pytest.raises(ValidationError) as exc_info:
        request_model.model_validate({field_name: "x" * (maximum_length + 1)})

    assert any(
        error["loc"] == (field_name,) and error["type"] == "string_too_long"
        for error in exc_info.value.errors()
    )
