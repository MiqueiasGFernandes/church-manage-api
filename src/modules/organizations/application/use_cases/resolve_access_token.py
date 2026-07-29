from modules.organizations.application.dto.auth import (
    AuthenticatedUser,
)
from modules.organizations.application.errors.auth import (
    InvalidAccessTokenError,
)
from modules.organizations.application.ports.auth import (
    ITokenService,
)
from modules.organizations.application.ports.registration_services import (
    IClock,
    IUnitOfWork,
)
from modules.organizations.application.repositories.auth_repository import (
    IAuthRepository,
)
from modules.organizations.domain.model import UserStatus
from modules.organizations.domain.use_cases.resolve_access_token import IResolveAccessToken


class ResolveAccessToken(IResolveAccessToken):
    def __init__(
        self,
        repository: IAuthRepository,
        unit_of_work: IUnitOfWork,
        tokens: ITokenService,
        clock: IClock,
    ) -> None:
        self._repository, self._unit_of_work = repository, unit_of_work
        self._tokens, self._clock = tokens, clock

    async def execute(self, token: str) -> AuthenticatedUser:
        try:
            user_id, session_id = self._tokens.decode_access(token, self._clock.now())
        except ValueError as exc:
            raise InvalidAccessTokenError("Access token inválido ou expirado.") from exc
        async with self._unit_of_work:
            session = await self._repository.find_session_by_id(session_id)
            user = await self._repository.find_user_by_id(user_id)
            if session is None or session.user_id != user_id or session.revoked_at is not None:
                raise InvalidAccessTokenError("Access token inválido ou expirado.")
            if user is None or user.status is not UserStatus.ACTIVE:
                raise InvalidAccessTokenError("Access token inválido ou expirado.")
        return AuthenticatedUser(user_id, session_id)
