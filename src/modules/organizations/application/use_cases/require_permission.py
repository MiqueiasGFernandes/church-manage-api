from uuid import UUID

from modules.organizations.application.dto.auth import (
    AuthenticatedUser,
)
from modules.organizations.application.errors.auth import (
    ChurchAccessDeniedError,
    PermissionDeniedError,
)
from modules.organizations.application.ports.registration_services import (
    IClock,
    IUnitOfWork,
)
from modules.organizations.application.repositories.auth_repository import (
    IAuthRepository,
    SecurityAuditEvent,
)
from modules.organizations.application.use_cases.permissions import ROLE_PERMISSIONS
from modules.organizations.domain.model import MembershipStatus
from modules.organizations.domain.use_cases.require_permission import IRequirePermission


class RequirePermission(IRequirePermission):
    def __init__(
        self, repository: IAuthRepository, unit_of_work: IUnitOfWork, clock: IClock
    ) -> None:
        self._repository, self._unit_of_work, self._clock = repository, unit_of_work, clock

    async def execute(self, actor: AuthenticatedUser, church_id: UUID, permission: str) -> None:
        denied_error: ChurchAccessDeniedError | PermissionDeniedError | None = None
        async with self._unit_of_work:
            membership = next(
                (
                    item
                    for item in await self._repository.memberships_for_user(actor.user_id)
                    if item.church_id.value == church_id
                ),
                None,
            )
            if membership is None or membership.status is not MembershipStatus.ACTIVE:
                denied_error = ChurchAccessDeniedError("Acesso à igreja negado.")
            elif permission not in ROLE_PERMISSIONS.get(membership.role.value, frozenset()):
                denied_error = PermissionDeniedError("Permissão insuficiente para esta operação.")
            if denied_error is not None:
                await self._repository.add_audit_event(
                    SecurityAuditEvent(
                        "AUTHORIZATION_DENIED",
                        self._clock.now(),
                        actor_user_id=actor.user_id,
                        church_id=church_id,
                        session_id=actor.session_id,
                    )
                )
                await self._unit_of_work.commit()
        if denied_error is not None:
            raise denied_error
