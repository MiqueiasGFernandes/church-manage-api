from typing import Protocol

from modules.organizations.application.dto.auth import (
    AuthenticatedUser,
    CurrentUserOutput,
)


class IGetCurrentUser(Protocol):
    async def execute(self, actor: AuthenticatedUser) -> CurrentUserOutput: ...
