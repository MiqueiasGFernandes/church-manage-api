from modules.organizations.application.errors.auth import InvalidPasswordError


def ensure_valid_password(password: str, email: str) -> None:
    if len(password) < 10 or password.casefold() == email.strip().casefold():
        raise InvalidPasswordError(
            "A senha deve ter ao menos 10 caracteres e não pode ser igual ao e-mail."
        )
