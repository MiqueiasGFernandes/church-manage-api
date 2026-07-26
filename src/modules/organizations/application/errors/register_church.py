class RegistrationError(Exception):
    code = "REGISTRATION_ERROR"


class TermsNotAcceptedError(RegistrationError):
    code = "TERMS_NOT_ACCEPTED"


class PasswordMismatchError(RegistrationError):
    code = "PASSWORD_MISMATCH"


class WeakPasswordError(RegistrationError):
    code = "WEAK_PASSWORD"


class UserEmailAlreadyExistsError(RegistrationError):
    code = "USER_EMAIL_ALREADY_EXISTS"


class ChurchSlugAlreadyExistsError(RegistrationError):
    code = "CHURCH_SLUG_ALREADY_EXISTS"


class ChurchDocumentAlreadyExistsError(RegistrationError):
    code = "CHURCH_DOCUMENT_ALREADY_EXISTS"
