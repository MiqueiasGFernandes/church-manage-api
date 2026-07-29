class AuthenticationError(Exception):
    code = "AUTHENTICATION_ERROR"


class InvalidEmailVerificationTokenError(AuthenticationError):
    code = "AUTH_EMAIL_VERIFICATION_TOKEN_INVALID"


class InvalidCredentialsError(AuthenticationError):
    code = "AUTH_INVALID_CREDENTIALS"


class EmailNotVerifiedError(AuthenticationError):
    code = "AUTH_EMAIL_NOT_VERIFIED"


class InvalidAccessTokenError(AuthenticationError):
    code = "AUTH_ACCESS_TOKEN_INVALID"


class InvalidRefreshTokenError(AuthenticationError):
    code = "AUTH_REFRESH_TOKEN_INVALID"


class SessionRevokedError(AuthenticationError):
    code = "AUTH_SESSION_REVOKED"


class PermissionDeniedError(AuthenticationError):
    code = "AUTH_PERMISSION_DENIED"


class ChurchAccessDeniedError(AuthenticationError):
    code = "AUTH_CHURCH_ACCESS_DENIED"


class SessionNotFoundError(AuthenticationError):
    code = "AUTH_SESSION_NOT_FOUND"


class RateLimitExceededError(AuthenticationError):
    code = "AUTH_RATE_LIMIT_EXCEEDED"


class InvalidPasswordResetTokenError(AuthenticationError):
    code = "AUTH_PASSWORD_RESET_TOKEN_INVALID"


class InvalidPasswordError(AuthenticationError):
    code = "AUTH_PASSWORD_INVALID"
