import time
from http import HTTPStatus

import allure
import pytest
from faker import Faker

from src.schemas.auth_schema import ResetPasswordResponseSchema

fake = Faker()

EXPECTED_MESSAGE = "Password reset request processed"


@pytest.mark.auth
@allure.feature("Authentication")
@allure.story("Reset Password")
class TestResetPassword:

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Reset Password: valid email → 200 + expected message")
    async def test_reset_password_valid_email(self, api_client) -> None:
        response = await api_client.post(
            "/reset_password",
            json={"email": fake.email()},
        )

        assert response.status_code == HTTPStatus.OK.value
        body = response.json()
        assert body.message == EXPECTED_MESSAGE

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Reset Password: with org_name → 200")
    async def test_reset_password_with_org_name(
        self,
        api_client,
        admin_credentials,
    ) -> None:
        response = await api_client.post(
            "/reset_password",
            json={
                "email": fake.email(),
                "org_name": admin_credentials["org_name"],
            },
        )
        assert response.status_code == HTTPStatus.OK.value

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Reset Password: non-existent email → 200 (anti-enumeration)")
    async def test_reset_password_nonexistent_email(self, api_client) -> None:
        response = await api_client.post(
            "/reset_password",
            json={"email": fake.email()},
        )
        assert response.status_code == HTTPStatus.OK.value

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Reset Password: two different emails return identical response")
    async def test_reset_password_same_response(self, api_client) -> None:
        first = await api_client.post("/reset_password", json={"email": fake.email()})
        second = await api_client.post("/reset_password", json={"email": fake.email()})

        assert first.status_code == second.status_code
        assert first.json() == second.json()

    @pytest.mark.asyncio
    @pytest.mark.security
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Reset Password: timing difference < 500ms (anti-timing-attack)")
    async def test_reset_password_no_timing_leak(self, api_client) -> None:
        start = time.monotonic()
        await api_client.post("/reset_password", json={"email": fake.email()})
        first_ms = time.monotonic() - start

        start = time.monotonic()
        await api_client.post("/reset_password", json={"email": fake.email()})
        second_ms = time.monotonic() - start

        diff_ms = abs(first_ms - second_ms) * 1000
        assert diff_ms < 500, f"Timing difference {diff_ms:.0f}ms may reveal account existence"

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Reset Password: missing email → 400 or 422")
    async def test_reset_password_missing_email(self, api_client) -> None:
        response = await api_client.post("/reset_password", json={"org_name": "QA"})
        assert response.status_code in (
            HTTPStatus.BAD_REQUEST.value,
            HTTPStatus.UNPROCESSABLE_ENTITY.value,
        )

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Reset Password: empty body → 400 or 422")
    async def test_reset_password_empty_body(self, api_client) -> None:
        response = await api_client.post("/reset_password", json={})
        assert response.status_code in (
            HTTPStatus.BAD_REQUEST.value,
            HTTPStatus.UNPROCESSABLE_ENTITY.value,
        )

    @pytest.mark.asyncio
    @pytest.mark.slow
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Reset Password: rate limit → 429 after repeated requests")
    async def test_reset_password_rate_limit_429(self, api_client) -> None:
        email = fake.email()
        status_codes = []

        for _ in range(15):
            response = await api_client.post("/reset_password", json={"email": email})
            status_codes.append(response.status_code)
            if response.status_code == HTTPStatus.TOO_MANY_REQUESTS.value:
                break

        assert HTTPStatus.TOO_MANY_REQUESTS.value in status_codes

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Reset Password: response must not leak user data")
    async def test_reset_password_no_user_data_leak(self, api_client) -> None:
        response = await api_client.post("/reset_password", json={"email": fake.email()})
        body = response.json()

        if isinstance(body, dict):
            sensitive_keys = {"token", "accessToken", "password", "id", "email"}
            assert not sensitive_keys.intersection(body.keys())