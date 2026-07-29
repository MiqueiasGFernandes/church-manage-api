from typing import Protocol

from modules.organizations.application.dto.auth import (
    AuthenticatedUser,
)


class ILogoutSession(Protocol):
    async def execute(self, actor: AuthenticatedUser) -> None: ...
