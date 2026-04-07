from http import HTTPStatus

import allure
import pytest
from faker import Faker

from src.schemas.auth_schema import MessageErrorSchema

fake = Faker()


@pytest.mark.auth
@pytest.mark.security
@allure.feature("Authentication")
@allure.story("Login – Security")
class TestLoginSecurity:

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Security: unknown orgName → 400/401/403")
    async def test_unknown_org_name(self, auth_client) -> None:
        response = await auth_client.login(
            identity=fake.email(),
            password=fake.password(),
            org_name=fake.company(),
        )
        assert response.status_code in (
            HTTPStatus.BAD_REQUEST.value,
            HTTPStatus.UNAUTHORIZED.value,
            HTTPStatus.FORBIDDEN.value,
            HTTPStatus.TOO_MANY_REQUESTS.value,
        )

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Security: password not returned in response body")
    async def test_password_not_in_response(
        self,
        auth_client,
        admin_credentials,
    ) -> None:
        response = await auth_client.login(**admin_credentials)
        assert admin_credentials["password"] not in response.text

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Security: SQL injection in identity field → not 500")
    async def test_sql_injection_in_identity(
        self,
        auth_client,
        admin_credentials,
    ) -> None:
        response = await auth_client.login(
            identity="' OR '1'='1",
            password="password",
            org_name=admin_credentials["org_name"],
        )
        assert response.status_code != HTTPStatus.INTERNAL_SERVER_ERROR.value

    @pytest.mark.asyncio
    @pytest.mark.slow
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Security: brute force protection → 429 after N failed attempts")
    async def test_brute_force_lockout(
        self,
        api_client,
        admin_credentials,
    ) -> None:
        status_codes = []
        for _ in range(10):
            response = await api_client.post(
                "/login",
                json={
                    "orgName": admin_credentials["org_name"],
                    "identity": fake.email(),
                    "password": "wrong_password",
                },
            )
            status_codes.append(response.status_code)
            if response.status_code == HTTPStatus.TOO_MANY_REQUESTS.value:
                break

        assert HTTPStatus.TOO_MANY_REQUESTS.value in status_codes

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Security: error message does not reveal if username exists")
    async def test_error_message_does_not_reveal_username(
        self,
        auth_client,
        admin_credentials,
    ) -> None:
        non_existent_response = await auth_client.login(
            identity=fake.email(),
            password=fake.password(),
            org_name=admin_credentials["org_name"],
        )

        wrong_password_response = await auth_client.login(
            identity=admin_credentials["identity"],
            password="wrong_password_!@#$",
            org_name=admin_credentials["org_name"],
        )

        if (
            non_existent_response.status_code == HTTPStatus.TOO_MANY_REQUESTS.value
            or wrong_password_response.status_code == HTTPStatus.TOO_MANY_REQUESTS.value
        ):
            pytest.skip("Rate limit hit — skipping message comparison")

        assert non_existent_response.status_code == HTTPStatus.BAD_REQUEST.value
        assert wrong_password_response.status_code == HTTPStatus.BAD_REQUEST.value

        body1 = MessageErrorSchema.model_validate(non_existent_response.json())
        body2 = MessageErrorSchema.model_validate(wrong_password_response.json())
        assert body1.message == body2.message

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Security: existing user with wrong org credentials → 400")
    async def test_existing_user_wrong_org_credentials(
        self,
        auth_client,
        admin_credentials,
    ) -> None:
        response = await auth_client.login(
            identity="AutomationUser",
            password=admin_credentials["password"],
            org_name=admin_credentials["org_name"],
        )

        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS.value:
            pytest.skip("Rate limit hit")

        assert response.status_code == HTTPStatus.BAD_REQUEST.value