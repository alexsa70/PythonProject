from http import HTTPStatus
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

@pytest.mark.auth
@allure.feature("Authentication")
@allure.story("Login – Positive")
class TestLoginPositive:

    @pytest.mark.asyncio
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "role_name, credentials_fixture",
        [
            ("Admin", "admin_credentials"),
            ("User", "user_credentials"),
        ],
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Login: valid credentials ({role_name}) → 200 + token")
    async def test_login_valid_credentials_by_role(
        self,
        request,
        auth_client,
        role_name: str,
        credentials_fixture: str,
    ) -> None:
        credentials = request.getfixturevalue(credentials_fixture)

        with allure.step(f"Send login request with valid {role_name} credentials"):
            response = await auth_client.login(**credentials)

        with allure.step("Verify status code is 200"):
            assert_status_code(response, HTTPStatus.OK.value   )

        with allure.step("Validate login response schema"):
            parsed = AuthResponseSchema.model_validate(response.json())

        with allure.step("Verify token and user data exist"):
            assert parsed.token
            assert parsed.user.id
            assert parsed.org.id

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Login: otp_code='' when MFA disabled → 200")
    async def test_login_otp_empty_string_mfa_disabled(
        self,
        auth_client,
        admin_credentials,
    ) -> None:
        with allure.step("Send login request with empty otp_code"):
            response = await auth_client.login(
                identity=admin_credentials["identity"],
                password=admin_credentials["password"],
                org_name=admin_credentials["org_name"],
                otp_code="",
            )

        with allure.step("Verify status code is 200"):
            assert_status_code(response, 200)

        with allure.step("Validate login response schema"):
            parsed = AuthResponseSchema.model_validate(response.json())
            assert parsed.token

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Login: username is case-insensitive (if supported) → 200")
    async def test_login_username_case_insensitive(
        self,
        auth_client,
        admin_credentials,
        admin_auth_context
    ) -> None:
        with allure.step("Send login request with uppercase identity"):
            response = await auth_client.login(
                identity=admin_auth_context.user.user_name.upper(),
                password=admin_credentials["password"],
                org_name=admin_credentials["org_name"],
            )

        with allure.step("Verify status code is 200"):
            assert_status_code(response, HTTPStatus.OK.value)

        with allure.step("Validate login response schema"):
            parsed = AuthResponseSchema.model_validate(response.json())
            assert parsed.token

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Login: response contains refresh_token and expires_in")
    async def test_login_verify_response_values(
        self,
        auth_client,
        admin_credentials,
    ) -> None:
        with allure.step("Send login request"):
            response = await auth_client.login(**admin_credentials)

        with allure.step("Verify status code is 200"):
            assert_status_code(response, HTTPStatus.OK.value)

        with allure.step("Validate login response schema"):
            parsed = AuthResponseSchema.model_validate(response.json())

        with allure.step("Verify refresh token and expires_in"):
            assert parsed.refresh_token
            assert parsed.expires_in