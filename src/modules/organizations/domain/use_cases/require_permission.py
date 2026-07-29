from typing import Protocol
from uuid import UUID

from modules.organizations.application.dto.auth import (
    AuthenticatedUser,
)


class IRequirePermission(Protocol):
    async def execute(self, actor: AuthenticatedUser, church_id: UUID, permission: str) -> None: ...
