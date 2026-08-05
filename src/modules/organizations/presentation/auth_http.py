from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from modules.organizations.application.dto.auth import AuthenticatedUser
from modules.organizations.application.errors.auth import (
    AuthenticationError,
    ChurchAccessDeniedError,
    EmailNotVerifiedError,
    HumanChallengeFailedError,
    HumanChallengeUnavailableError,
    InvalidAccessTokenError,
    InvalidCredentialsError,
    InvalidPasswordError,
    PermissionDeniedError,
    RateLimitExceededError,
    SessionNotFoundError,
)
from modules.organizations.application.ports.auth import IRateLimiter, RateLimitAction
from modules.organizations.application.ports.human_challenge import (
    HumanChallengeAction,
    IHumanChallengeVerifier,
)
from modules.organizations.domain.use_cases.authenticate_user import IAuthenticateUser
from modules.organizations.domain.use_cases.change_password import IChangePassword
from modules.organizations.domain.use_cases.get_current_user import IGetCurrentUser
from modules.organizations.domain.use_cases.list_user_sessions import IListUserSessions
from modules.organizations.domain.use_cases.logout_all_sessions import ILogoutAllSessions
from modules.organizations.domain.use_cases.logout_session import ILogoutSession
from modules.organizations.domain.use_cases.refresh_session import IRefreshSession
from modules.organizations.domain.use_cases.request_password_reset import IRequestPasswordReset
from modules.organizations.domain.use_cases.require_permission import IRequirePermission
from modules.organizations.domain.use_cases.resend_email_verification import (
    IResendEmailVerification,
)
from modules.organizations.domain.use_cases.reset_password import IResetPassword
from modules.organizations.domain.use_cases.resolve_access_token import IResolveAccessToken
from modules.organizations.domain.use_cases.revoke_user_session import IRevokeUserSession
from modules.organizations.domain.use_cases.verify_email import IVerifyEmail

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
church_router = APIRouter(prefix="/api/v1/churches", tags=["authorization"])


class VerifyEmailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: str = Field(min_length=32, max_length=128)


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(max_length=254)
    password: str = Field(min_length=1, max_length=128)
    captcha_token: str = Field(min_length=1, max_length=2048)


class EmailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(max_length=254)


class ForgotPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(max_length=254)
    captcha_token: str = Field(min_length=1, max_length=2048)


class ResetPasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: str = Field(min_length=32, max_length=128)
    new_password: str = Field(min_length=10, max_length=128)


class ChangePasswordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=10, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class ChurchAccessResponse(BaseModel):
    church_id: UUID
    role: str
    permissions: tuple[str, ...]


class CurrentUserResponse(BaseModel):
    user_id: UUID
    name: str
    email: str
    churches: tuple[ChurchAccessResponse, ...]


class UserSessionResponse(BaseModel):
    session_id: UUID
    created_at: datetime
    expires_at: datetime
    current: bool


async def get_verify_email() -> IVerifyEmail:
    raise RuntimeError("Dependência não configurada.")


async def get_authenticate() -> IAuthenticateUser:
    raise RuntimeError("Dependência não configurada.")


async def get_refresh_session() -> IRefreshSession:
    raise RuntimeError("Dependência não configurada.")


async def get_resolve_access() -> IResolveAccessToken:
    raise RuntimeError("Dependência não configurada.")


async def get_current_user() -> IGetCurrentUser:
    raise RuntimeError("Dependência não configurada.")


async def get_logout_session() -> ILogoutSession:
    raise RuntimeError("Dependência não configurada.")


async def get_logout_all_sessions() -> ILogoutAllSessions:
    raise RuntimeError("Dependência não configurada.")


async def get_list_sessions() -> IListUserSessions:
    raise RuntimeError("Dependência não configurada.")


async def get_revoke_session() -> IRevokeUserSession:
    raise RuntimeError("Dependência não configurada.")


async def get_resend_email_verification() -> IResendEmailVerification:
    raise RuntimeError("Dependência não configurada.")


async def get_request_password_reset() -> IRequestPasswordReset:
    raise RuntimeError("Dependência não configurada.")


async def get_reset_password() -> IResetPassword:
    raise RuntimeError("Dependência não configurada.")


async def get_change_password() -> IChangePassword:
    raise RuntimeError("Dependência não configurada.")


async def get_require_permission() -> IRequirePermission:
    raise RuntimeError("Dependência não configurada.")


async def get_rate_limiter() -> IRateLimiter:
    raise RuntimeError("Dependência não configurada.")


async def get_human_challenge_verifier() -> IHumanChallengeVerifier:
    raise RuntimeError("Dependência não configurada.")


def client_address(request: Request) -> str:
    return request.client.host if request.client is not None else "unknown"


async def current_actor(
    authorization: Annotated[str | None, Header()] = None,
    resolver: IResolveAccessToken = Depends(get_resolve_access),
) -> AuthenticatedUser:
    if authorization is None or not authorization.startswith("Bearer "):
        raise InvalidAccessTokenError("Token de acesso ausente ou inválido.")
    return await resolver.execute(authorization.removeprefix("Bearer "))


def set_refresh_cookie(response: Response, refresh_token: str, secure: bool) -> None:
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=14 * 24 * 3600,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/api/v1/auth",
    )


@router.post("/verify-email", status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(
    body: VerifyEmailRequest,
    request: Request,
    use_case: IVerifyEmail = Depends(get_verify_email),
    rate_limiter: IRateLimiter = Depends(get_rate_limiter),
) -> Response:
    await rate_limiter.ensure_allowed(
        RateLimitAction.VERIFY_EMAIL, f"verify-email:{client_address(request)}"
    )
    await use_case.execute(body.token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/verify-email/resend", status_code=status.HTTP_204_NO_CONTENT)
async def resend_email_verification(
    body: EmailRequest,
    request: Request,
    use_case: IResendEmailVerification = Depends(get_resend_email_verification),
    rate_limiter: IRateLimiter = Depends(get_rate_limiter),
) -> Response:
    await rate_limiter.ensure_allowed(
        RateLimitAction.RESEND_EMAIL_VERIFICATION,
        f"resend-verification:{client_address(request)}:{body.email.strip().casefold()}",
    )
    await use_case.execute(body.email)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
async def forgot_password(
    body: ForgotPasswordRequest,
    request: Request,
    use_case: IRequestPasswordReset = Depends(get_request_password_reset),
    rate_limiter: IRateLimiter = Depends(get_rate_limiter),
    human_challenge: IHumanChallengeVerifier = Depends(get_human_challenge_verifier),
) -> Response:
    await rate_limiter.ensure_allowed(
        RateLimitAction.FORGOT_PASSWORD,
        f"forgot-password:{client_address(request)}:{body.email.strip().casefold()}",
    )
    await human_challenge.ensure_valid(body.captcha_token, HumanChallengeAction.PASSWORD_RECOVERY)
    await use_case.execute(body.email)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    body: ResetPasswordRequest,
    request: Request,
    use_case: IResetPassword = Depends(get_reset_password),
    rate_limiter: IRateLimiter = Depends(get_rate_limiter),
) -> Response:
    await rate_limiter.ensure_allowed(
        RateLimitAction.RESET_PASSWORD, f"reset-password:{client_address(request)}"
    )
    await use_case.execute(body.token, body.new_password)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    use_case: IAuthenticateUser = Depends(get_authenticate),
    rate_limiter: IRateLimiter = Depends(get_rate_limiter),
    human_challenge: IHumanChallengeVerifier = Depends(get_human_challenge_verifier),
) -> TokenResponse:
    await rate_limiter.ensure_allowed(
        RateLimitAction.LOGIN,
        f"login:{client_address(request)}:{body.email.strip().casefold()}",
    )
    await human_challenge.ensure_valid(body.captcha_token, HumanChallengeAction.LOGIN)
    result = await use_case.execute(body.email, body.password)
    set_refresh_cookie(response, result.refresh_token, bool(request.app.state.auth_cookie_secure))
    return TokenResponse(
        access_token=result.access_token, token_type=result.token_type, expires_in=result.expires_in
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    response: Response,
    use_case: IRefreshSession = Depends(get_refresh_session),
    rate_limiter: IRateLimiter = Depends(get_rate_limiter),
) -> TokenResponse:
    origin = request.headers.get("origin")
    if origin is not None and origin not in request.app.state.cors_allowed_origins:
        raise PermissionDeniedError("Origem não permitida para renovação da sessão.")
    await rate_limiter.ensure_allowed(RateLimitAction.REFRESH, f"refresh:{client_address(request)}")
    token = request.cookies.get("refresh_token")
    if token is None:
        from modules.organizations.application.errors.auth import InvalidRefreshTokenError

        raise InvalidRefreshTokenError("Refresh token inválido.")
    result = await use_case.execute(token)
    set_refresh_cookie(response, result.refresh_token, bool(request.app.state.auth_cookie_secure))
    return TokenResponse(
        access_token=result.access_token, token_type=result.token_type, expires_in=result.expires_in
    )


@router.get("/me", response_model=CurrentUserResponse)
async def me(
    actor: AuthenticatedUser = Depends(current_actor),
    use_case: IGetCurrentUser = Depends(get_current_user),
) -> CurrentUserResponse:
    result = await use_case.execute(actor)
    return CurrentUserResponse(
        user_id=result.user_id,
        name=result.name,
        email=result.email,
        churches=tuple(
            ChurchAccessResponse(
                church_id=item.church_id, role=item.role, permissions=item.permissions
            )
            for item in result.churches
        ),
    )


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    body: ChangePasswordRequest,
    request: Request,
    actor: AuthenticatedUser = Depends(current_actor),
    use_case: IChangePassword = Depends(get_change_password),
    rate_limiter: IRateLimiter = Depends(get_rate_limiter),
) -> Response:
    await rate_limiter.ensure_allowed(
        RateLimitAction.CHANGE_PASSWORD,
        f"change-password:{client_address(request)}:{actor.user_id}",
    )
    await use_case.execute(actor, body.current_password, body.new_password)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    actor: AuthenticatedUser = Depends(current_actor),
    use_case: ILogoutSession = Depends(get_logout_session),
) -> Response:
    await use_case.execute(actor)
    response.delete_cookie("refresh_token", path="/api/v1/auth")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    response: Response,
    actor: AuthenticatedUser = Depends(current_actor),
    use_case: ILogoutAllSessions = Depends(get_logout_all_sessions),
) -> Response:
    await use_case.execute(actor)
    response.delete_cookie("refresh_token", path="/api/v1/auth")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/sessions", response_model=tuple[UserSessionResponse, ...])
async def list_sessions(
    actor: AuthenticatedUser = Depends(current_actor),
    use_case: IListUserSessions = Depends(get_list_sessions),
) -> tuple[UserSessionResponse, ...]:
    result = await use_case.execute(actor)
    return tuple(
        UserSessionResponse(
            session_id=item.session_id,
            created_at=item.created_at,
            expires_at=item.expires_at,
            current=item.current,
        )
        for item in result
    )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_session(
    session_id: UUID,
    actor: AuthenticatedUser = Depends(current_actor),
    use_case: IRevokeUserSession = Depends(get_revoke_session),
) -> Response:
    await use_case.execute(actor, session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@church_router.get("/{church_id}/me", response_model=CurrentUserResponse)
async def church_me(
    church_id: UUID,
    actor: AuthenticatedUser = Depends(current_actor),
    authorization: IRequirePermission = Depends(get_require_permission),
    current: IGetCurrentUser = Depends(get_current_user),
) -> CurrentUserResponse:
    await authorization.execute(actor, church_id, "church:read")
    result = await current.execute(actor)
    return CurrentUserResponse(
        user_id=result.user_id,
        name=result.name,
        email=result.email,
        churches=tuple(
            ChurchAccessResponse(
                church_id=item.church_id, role=item.role, permissions=item.permissions
            )
            for item in result.churches
            if item.church_id == church_id
        ),
    )


async def auth_error_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AuthenticationError)
    if isinstance(exc, SessionNotFoundError):
        status_code = 404
    elif isinstance(exc, InvalidPasswordError):
        status_code = 422
    elif isinstance(exc, RateLimitExceededError):
        status_code = 429
    elif isinstance(exc, HumanChallengeUnavailableError):
        status_code = 503
    elif isinstance(exc, HumanChallengeFailedError):
        status_code = 422
    elif isinstance(exc, (EmailNotVerifiedError, PermissionDeniedError, ChurchAccessDeniedError)):
        status_code = 403
    else:
        status_code = 401
    if isinstance(exc, InvalidCredentialsError):
        detail = "E-mail ou senha inválidos."
    else:
        detail = str(exc)
    request.state.error_code = exc.code
    return JSONResponse(
        status_code=status_code, content={"error": {"code": exc.code, "message": detail}}
    )
