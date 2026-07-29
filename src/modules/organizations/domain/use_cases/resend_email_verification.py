from typing import Protocol


class IResendEmailVerification(Protocol):
    async def execute(self, email: str) -> None: ...
