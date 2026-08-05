import httpx
import pytest

from modules.organizations.application.errors.auth import (
    HumanChallengeFailedError,
    HumanChallengeUnavailableError,
)
from modules.organizations.application.ports.human_challenge import HumanChallengeAction
from modules.organizations.infrastructure.turnstile import TurnstileHumanChallengeVerifier


async def test_accepts_valid_turnstile_token_for_expected_action_and_hostname() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://challenges.cloudflare.com/turnstile/v0/siteverify"
        return httpx.Response(
            200,
            json={"success": True, "action": "login", "hostname": "app.reuniva.com.br"},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        verifier = TurnstileHumanChallengeVerifier(
            secret="secret", allowed_hostnames=("app.reuniva.com.br",), client=client
        )

        await verifier.ensure_valid("valid-token", HumanChallengeAction.LOGIN)


@pytest.mark.parametrize(
    "response",
    [
        {"success": False, "action": "login", "hostname": "app.reuniva.com.br"},
        {"success": True, "action": "registration", "hostname": "app.reuniva.com.br"},
        {"success": True, "action": "login", "hostname": "evil.example.com"},
    ],
)
async def test_rejects_invalid_action_or_hostname(response: dict[str, object]) -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=response)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        verifier = TurnstileHumanChallengeVerifier(
            secret="secret", allowed_hostnames=("app.reuniva.com.br",), client=client
        )

        with pytest.raises(HumanChallengeFailedError):
            await verifier.ensure_valid("invalid-token", HumanChallengeAction.LOGIN)


async def test_reports_turnstile_as_unavailable_without_exposing_provider_details() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("secret provider detail")

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        verifier = TurnstileHumanChallengeVerifier(
            secret="secret", allowed_hostnames=("app.reuniva.com.br",), client=client
        )

        with pytest.raises(HumanChallengeUnavailableError, match="Verificação indisponível"):
            await verifier.ensure_valid("token", HumanChallengeAction.LOGIN)
