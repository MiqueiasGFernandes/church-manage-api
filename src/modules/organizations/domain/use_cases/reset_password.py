from typing import Protocol


class IResetPassword(Protocol):
    async def execute(self, token: str, new_password: str) -> None: ...
