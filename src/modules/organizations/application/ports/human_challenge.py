from enum import StrEnum
from typing import Protocol


class HumanChallengeAction(StrEnum):
    LOGIN = "login"
    REGISTRATION = "registration"
    PASSWORD_RECOVERY = "password_recovery"


class IHumanChallengeVerifier(Protocol):
    async def ensure_valid(self, token: str, action: HumanChallengeAction) -> None: ...
