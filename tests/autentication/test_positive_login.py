import pytest
import allure

from src.utils.assertions import assert_status_code
from src.schemas.auth_schema import AuthResponseSchema


@pytest.mark.asyncio
@allure.severity(allure.severity_level.BLOCKER)
@allure.title("Login with valid credentials")
async def test_login(auth_client, user_credentials):

    with allure.step("Send login request with valid credentials"):
        response = await auth_client.login(
            identity=user_credentials["identity"],
            password=user_credentials["password"],
            org_name=user_credentials["org_name"],
        )

    with allure.step("Verify status code is 200"):
        assert_status_code(response, 200)

    with allure.step("Validate login response schema"):
        response_json = response.json()
        parsed = AuthResponseSchema.model_validate(response_json)

    with allure.step("Verify token and user data"):
        assert parsed.token
        assert parsed.user.id
        assert parsed.user.email == user_credentials["identity"]