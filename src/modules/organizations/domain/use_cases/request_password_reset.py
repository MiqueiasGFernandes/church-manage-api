from typing import Protocol


class IRequestPasswordReset(Protocol):
    async def execute(self, email: str) -> None: ...
