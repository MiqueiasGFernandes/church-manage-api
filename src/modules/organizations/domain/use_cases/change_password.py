from typing import Protocol

from modules.organizations.application.dto.auth import (
    AuthenticatedUser,
)


class IChangePassword(Protocol):
    async def execute(
        self,
        actor: AuthenticatedUser,
        current_password: str,
        new_password: str,
    ) -> None: ...
