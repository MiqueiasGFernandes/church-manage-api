from typing import Protocol

from modules.organizations.application.dto.auth import (
    AuthenticatedUser,
)


class ILogoutAllSessions(Protocol):
    async def execute(self, actor: AuthenticatedUser) -> None: ...
