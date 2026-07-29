from modules.organizations.application.dto.auth import (
    AuthenticatedUser,
    UserSessionOutput,
)
from modules.organizations.application.ports.registration_services import (
    IClock,
    IUnitOfWork,
)
from modules.organizations.application.repositories.auth_repository import (
    IAuthRepository,
)
from modules.organizations.domain.use_cases.list_user_sessions import IListUserSessions


class ListUserSessions(IListUserSessions):
    def __init__(
        self, repository: IAuthRepository, unit_of_work: IUnitOfWork, clock: IClock
    ) -> None:
        self._repository, self._unit_of_work, self._clock = repository, unit_of_work, clock

    async def execute(self, actor: AuthenticatedUser) -> tuple[UserSessionOutput, ...]:
        now = self._clock.now()
        async with self._unit_of_work:
            sessions = await self._repository.sessions_for_user(actor.user_id)
        return tuple(
            UserSessionOutput(
                item.id, item.created_at, item.expires_at, item.id == actor.session_id
            )
            for item in sessions
            if item.revoked_at is None and item.expires_at > now
        )
