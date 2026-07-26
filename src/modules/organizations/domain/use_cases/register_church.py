from typing import Protocol

from modules.organizations.application.dto.register_church import (
    RegisterChurchInput,
    RegisterChurchOutput,
)


class IRegisterChurch(Protocol):
    async def execute(self, data: RegisterChurchInput) -> RegisterChurchOutput: ...
