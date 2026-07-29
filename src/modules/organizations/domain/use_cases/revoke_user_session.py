from typing import Protocol
from uuid import UUID

from modules.organizations.application.dto.auth import (
    AuthenticatedUser,
)


class IRevokeUserSession(Protocol):
    async def execute(self, actor: AuthenticatedUser, session_id: UUID) -> None: ...
