from typing import Protocol


class IVerifyEmail(Protocol):
    async def execute(self, token: str) -> None: ...
