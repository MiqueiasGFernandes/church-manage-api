from typing import Protocol

from modules.organizations.application.dto.auth import (
    TokenPair,
)


class IAuthenticateUser(Protocol):
    async def execute(self, email: str, password: str) -> TokenPair: ...
