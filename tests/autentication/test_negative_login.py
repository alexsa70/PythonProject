from http import HTTPStatus

import allure
import pytest
from faker import Faker

from src.schemas.auth_schema import MessageErrorSchema

fake = Faker()

EXPECTED_ERROR_MESSAGE = "User name or password incorrect."


@pytest.mark.auth
@allure.feature("Authentication")
@allure.story("Login – Negative")
class TestLoginNegative:

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Login: invalid password → 400 + error message")
    async def test_invalid_password(
        self,
        auth_client,
        admin_credentials,
    ) -> None:
        with allure.step("Send login request with invalid password"):
            response = await auth_client.login(
                identity=admin_credentials["identity"],
                password="wrong_password_!@#$",
                org_name=admin_credentials["org_name"],
            )

        with allure.step("Verify status code is 400"):
            assert response.status_code == HTTPStatus.BAD_REQUEST.value

        with allure.step("Validate error response"):
            body = MessageErrorSchema.model_validate(response.json())
            assert body.message == EXPECTED_ERROR_MESSAGE

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Login: invalid username → 400 + error message")
    async def test_invalid_username(
        self,
        auth_client,
        admin_credentials,
    ) -> None:
        with allure.step("Send login request with invalid username"):
            response = await auth_client.login(
                identity=fake.email(),
                password=fake.password(),
                org_name=admin_credentials["org_name"],
            )

        with allure.step("Verify status code is 400"):
            assert response.status_code == HTTPStatus.BAD_REQUEST.value

        with allure.step("Validate error response"):
            body = MessageErrorSchema.model_validate(response.json())
            assert body.message == EXPECTED_ERROR_MESSAGE

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Login: missing password field → 400 or 422")
    async def test_missing_password(
        self,
        api_client,
        admin_credentials,
    ) -> None:
        response = await api_client.post(
            "/login",
            json={
                "orgName": admin_credentials["org_name"],
                "identity": fake.email(),
            },
        )
        assert response.status_code in (
            HTTPStatus.BAD_REQUEST.value,
            HTTPStatus.UNPROCESSABLE_ENTITY.value,
        )

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Login: missing username field → 400 or 422")
    async def test_missing_username(
        self,
        api_client,
        admin_credentials,
    ) -> None:
        response = await api_client.post(
            "/login",
            json={
                "orgName": admin_credentials["org_name"],
                "password": fake.password(),
            },
        )
        assert response.status_code in (
            HTTPStatus.BAD_REQUEST.value,
            HTTPStatus.UNPROCESSABLE_ENTITY.value,
        )

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Login: missing orgName field → 400 or 422")
    async def test_missing_org_name(self, api_client) -> None:
        response = await api_client.post(
            "/login",
            json={
                "identity": fake.email(),
                "password": fake.password(),
            },
        )
        assert response.status_code in (
            HTTPStatus.BAD_REQUEST.value,
            HTTPStatus.UNPROCESSABLE_ENTITY.value,
        )

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Login: empty body → 400 or 422")
    async def test_empty_body(self, api_client) -> None:
        response = await api_client.post("/login", json={})
        assert response.status_code in (
            HTTPStatus.BAD_REQUEST.value,
            HTTPStatus.UNPROCESSABLE_ENTITY.value,
        )