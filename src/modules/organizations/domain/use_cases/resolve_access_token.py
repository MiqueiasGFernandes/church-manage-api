from typing import Protocol

from modules.organizations.application.dto.auth import (
    AuthenticatedUser,
)


class IResolveAccessToken(Protocol):
    async def execute(self, token: str) -> AuthenticatedUser: ...
