from typing import Protocol

from modules.organizations.application.dto.auth import (
    AuthenticatedUser,
    UserSessionOutput,
)


class IListUserSessions(Protocol):
    async def execute(self, actor: AuthenticatedUser) -> tuple[UserSessionOutput, ...]: ...
