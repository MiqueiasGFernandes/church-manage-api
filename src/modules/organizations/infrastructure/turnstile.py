import httpx
from pydantic import BaseModel, ConfigDict

from modules.organizations.application.errors.auth import (
    HumanChallengeFailedError,
    HumanChallengeUnavailableError,
)
from modules.organizations.application.ports.human_challenge import (
    HumanChallengeAction,
    IHumanChallengeVerifier,
)

SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


class TurnstileResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    success: bool
    action: str = ""
    hostname: str = ""


class TurnstileHumanChallengeVerifier(IHumanChallengeVerifier):
    def __init__(
        self,
        secret: str,
        allowed_hostnames: tuple[str, ...],
        client: httpx.AsyncClient,
    ) -> None:
        self._secret = secret
        self._allowed_hostnames = allowed_hostnames
        self._client = client

    async def ensure_valid(self, token: str, action: HumanChallengeAction) -> None:
        try:
            response = await self._client.post(
                SITEVERIFY_URL,
                json={"secret": self._secret, "response": token},
            )
            response.raise_for_status()
            result = TurnstileResponse.model_validate(response.json())
        except (httpx.HTTPError, ValueError) as exc:
            raise HumanChallengeUnavailableError(
                "Verificação indisponível no momento. Tente novamente."
            ) from exc

        if (
            not result.success
            or result.action != action.value
            or result.hostname not in self._allowed_hostnames
        ):
            raise HumanChallengeFailedError(
                "Não foi possível confirmar a verificação de segurança. Tente novamente."
            )


class AllowAllHumanChallengeVerifier(IHumanChallengeVerifier):
    async def ensure_valid(self, token: str, action: HumanChallengeAction) -> None:
        del action
        if not token.strip():
            raise HumanChallengeFailedError(
                "Não foi possível confirmar a verificação de segurança. Tente novamente."
            )
