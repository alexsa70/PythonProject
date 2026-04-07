import base64
import json
from http import HTTPStatus

import allure
import pytest

from src.schemas.auth_schema import AuthResponseSchema


def _decode_jwt_payload(token: str) -> dict:
    payload_b64 = token.split(".")[1]
    padding = 4 - len(payload_b64) % 4
    payload_b64 += "=" * (padding % 4)
    return json.loads(base64.urlsafe_b64decode(payload_b64))


@pytest.mark.auth
@allure.feature("Authentication")
@allure.story("Login – Token Validation")
class TestLoginTokenValidation:

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Token: access token has valid JWT 3-part structure")
    async def test_access_token_jwt_structure(
        self,
        auth_client,
        admin_credentials,
    ) -> None:
        response = await auth_client.login(**admin_credentials)

        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS.value:
            pytest.skip("Rate limit hit")

        assert response.status_code == HTTPStatus.OK.value

        body = AuthResponseSchema.model_validate(response.json())
        parts = body.token.split(".")

        assert len(parts) == 3
        assert parts[0].startswith("eyJ")

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Token: JWT payload contains required claims (sub, exp, iat)")
    async def test_jwt_payload_required_claims(
        self,
        auth_client,
        admin_credentials,
    ) -> None:
        response = await auth_client.login(**admin_credentials)

        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS.value:
            pytest.skip("Rate limit hit")

        assert response.status_code == HTTPStatus.OK.value

        body = AuthResponseSchema.model_validate(response.json())
        jwt_payload = _decode_jwt_payload(body.token)

        assert "sub" in jwt_payload
        assert "exp" in jwt_payload
        assert "iat" in jwt_payload
        assert isinstance(jwt_payload["exp"], int)
        assert isinstance(jwt_payload["iat"], int)