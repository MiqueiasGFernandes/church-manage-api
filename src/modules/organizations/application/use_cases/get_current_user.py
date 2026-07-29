from modules.organizations.application.dto.auth import (
    AuthenticatedUser,
    ChurchAccess,
    CurrentUserOutput,
)
from modules.organizations.application.errors.auth import (
    InvalidAccessTokenError,
)
from modules.organizations.application.ports.registration_services import (
    IUnitOfWork,
)
from modules.organizations.application.repositories.auth_repository import (
    IAuthRepository,
)
from modules.organizations.application.use_cases.permissions import ROLE_PERMISSIONS
from modules.organizations.domain.model import MembershipStatus
from modules.organizations.domain.use_cases.get_current_user import IGetCurrentUser


class GetCurrentUser(IGetCurrentUser):
    def __init__(self, repository: IAuthRepository, unit_of_work: IUnitOfWork) -> None:
        self._repository, self._unit_of_work = repository, unit_of_work

    async def execute(self, actor: AuthenticatedUser) -> CurrentUserOutput:
        async with self._unit_of_work:
            user = await self._repository.find_user_by_id(actor.user_id)
            if user is None:
                raise InvalidAccessTokenError("Access token inválido ou expirado.")
            memberships = await self._repository.memberships_for_user(actor.user_id)
        churches = tuple(
            ChurchAccess(
                item.church_id.value,
                item.role.value,
                tuple(sorted(ROLE_PERMISSIONS.get(item.role.value, frozenset()))),
            )
            for item in memberships
            if item.status is MembershipStatus.ACTIVE
        )
        return CurrentUserOutput(user.id.value, user.name, user.email.value, churches)
