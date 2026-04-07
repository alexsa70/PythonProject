from http import HTTPStatus

import allure
import pytest

from src.schemas.auth_schema import MessageErrorSchema
from src.utils.assertions import assert_status_code


@pytest.mark.auth
@pytest.mark.integration
@allure.feature("Authentication")
@allure.story("SSO Login")
class TestSSOLogin:

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("SSO: invalid code → 400 with message")
    async def test_sso_invalid_code_returns_400(
        self,
        auth_client,
        admin_credentials,
    ) -> None:
        with allure.step("Send SSO login request with invalid code"):
            response = await auth_client.sso_login(
                org_name=admin_credentials["org_name"],
                code="invalid_code_xyz",
                redirect_uri="https://app.kalsense.com/auth/callback",
                provider="google",
            )
            if response.status_code == 403:
                pytest.skip("SSO not enabled for this organization")

        with allure.step("Verify status code is 400"):
            assert_status_code(response, HTTPStatus.BAD_REQUEST.value)

        with allure.step("Validate error response schema"):
            body = MessageErrorSchema.model_validate(response.json())

        with allure.step("Verify error message exists"):
            assert body.message or body.detail

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("SSO: missing orgName → 400 or 422")
    async def test_sso_missing_org_name(self, api_client) -> None:
        with allure.step("Send SSO login request without orgName"):
            response = await api_client.post(
                "/sso_login",
                json={
                    "code": "some_code",
                    "redirect_uri": "https://app.kalsense.com/auth/callback",
                    "provider": "google",
                },
            )

        with allure.step("Verify status code is 400 or 422"):
            assert response.status_code in (
                HTTPStatus.BAD_REQUEST.value,
                HTTPStatus.UNPROCESSABLE_ENTITY.value,
            )

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("SSO: missing code → 400 or 422")
    async def test_sso_missing_code(self, api_client, admin_credentials) -> None:
        with allure.step("Send SSO login request without code"):
            response = await api_client.post(
                "/sso_login",
                json={
                    "orgName": admin_credentials["org_name"],
                    "redirect_uri": "https://app.kalsense.com/auth/callback",
                    "provider": "google",
                },
            )

        with allure.step("Verify status code is 400 or 422"):
            assert response.status_code in (
                HTTPStatus.BAD_REQUEST.value,
                HTTPStatus.UNPROCESSABLE_ENTITY.value,
            )

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("SSO: missing redirect_uri → 400 or 422")
    async def test_sso_missing_redirect_uri(self, api_client, admin_credentials) -> None:
        with allure.step("Send SSO login request without redirect_uri"):
            response = await api_client.post(
                "/sso_login",
                json={
                    "orgName": admin_credentials["org_name"],
                    "code": "some_code",
                    "provider": "google",
                },
            )

        with allure.step("Verify status code is 400 or 422"):
            assert response.status_code in (
                HTTPStatus.BAD_REQUEST.value,
                HTTPStatus.UNPROCESSABLE_ENTITY.value,
            )

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("SSO: missing provider → 400 or 422")
    async def test_sso_missing_provider(self, api_client, admin_credentials) -> None:
        with allure.step("Send SSO login request without provider"):
            response = await api_client.post(
                "/sso_login",
                json={
                    "orgName": admin_credentials["org_name"],
                    "code": "some_code",
                    "redirect_uri": "https://app.kalsense.com/auth/callback",
                },
            )

        with allure.step("Verify status code is 400 or 422"):
            assert response.status_code in (
                HTTPStatus.BAD_REQUEST.value,
                HTTPStatus.UNPROCESSABLE_ENTITY.value,
            )

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("SSO: unknown provider → 400 or 422")
    async def test_sso_unknown_provider(
        self,
        auth_client,
        admin_credentials,
    ) -> None:
        with allure.step("Send SSO login request with unknown provider"):
            response = await auth_client.sso_login(
                org_name=admin_credentials["org_name"],
                code="some_code",
                redirect_uri="https://app.kalsense.com/auth/callback",
                provider="unknown_provider_xyz",
            )
            if response.status_code == 403:
                pytest.skip("SSO not enabled for this organization")

        with allure.step("Verify status code is 400 or 422"):
            assert response.status_code in (
                HTTPStatus.BAD_REQUEST.value,
                HTTPStatus.UNPROCESSABLE_ENTITY.value,
            )

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("SSO: open redirect rejected → 400 or 422")
    async def test_sso_open_redirect_rejected(
        self,
        auth_client,
        admin_credentials,
    ) -> None:
        with allure.step("Send SSO login request with malicious redirect_uri"):
            response = await auth_client.sso_login(
                org_name=admin_credentials["org_name"],
                code="some_code",
                redirect_uri="https://attacker.com/steal",
                provider="google",
            )
            if response.status_code == 403:
                pytest.skip("SSO not enabled for this organization")

        with allure.step("Verify status code is 400 or 422"):
            assert response.status_code in (
                HTTPStatus.BAD_REQUEST.value,
                HTTPStatus.UNPROCESSABLE_ENTITY.value,
            )

    @pytest.mark.asyncio
    @pytest.mark.slow
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("SSO: rate limit → 429 after 50+ req/min")
    async def test_sso_rate_limit_429(
        self,
        api_client,
        admin_credentials,
    ) -> None:
        status_codes = []

        for _ in range(55):
            response = await api_client.post(
                "/sso_login",
                json={
                    "orgName": admin_credentials["org_name"],
                    "code": "some_code",
                    "redirect_uri": "https://app.kalsense.com/auth/callback",
                    "provider": "google",
                },
            )
            status_codes.append(response.status_code)

            if response.status_code == HTTPStatus.TOO_MANY_REQUESTS.value:
                break

        with allure.step("Verify at least one response returned 429"):
            assert HTTPStatus.TOO_MANY_REQUESTS.value in status_codes

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("SSO: SQL injection in orgName → not 500")
    async def test_sso_sql_injection(self, auth_client) -> None:
        with allure.step("Send SSO login request with SQL injection-like orgName"):
            response = await auth_client.sso_login(
                org_name="' OR '1'='1",
                code="some_code",
                redirect_uri="https://app.kalsense.com/auth/callback",
                provider="google",
            )

        with allure.step("Verify response is not 500"):
            assert response.status_code != HTTPStatus.INTERNAL_SERVER_ERROR.value

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("SSO: JWT not leaked in error response")
    async def test_sso_no_token_in_error(
        self,
        auth_client,
        admin_credentials,
    ) -> None:
        with allure.step("Send SSO login request with invalid code"):
            response = await auth_client.sso_login(
                org_name=admin_credentials["org_name"],
                code="invalid_code",
                redirect_uri="https://app.kalsense.com/auth/callback",
                provider="google",
            )

        with allure.step("Verify JWT token is not leaked in error response"):
            assert "eyJ" not in response.text