from typing import Protocol

from modules.organizations.application.dto.auth import (
    TokenPair,
)


class IRefreshSession(Protocol):
    async def execute(self, refresh_token: str) -> TokenPair: ...
