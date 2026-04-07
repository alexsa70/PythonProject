from http import HTTPStatus

import allure
import pytest

from src.schemas.auth_schema import MessageErrorSchema


@pytest.mark.auth
@allure.feature("Authentication")
@allure.story("MFA Flow")
class TestLoginMFAFlow:

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("MFA: OTP provided when MFA disabled → 400/422 + error message")
    async def test_otp_provided_when_mfa_disabled(
        self,
        auth_client,
        admin_credentials,
    ) -> None:
        response = await auth_client.login(
            identity=admin_credentials["identity"],
            password=admin_credentials["password"],
            org_name=admin_credentials["org_name"],
            otp_code="123456",
        )

        assert response.status_code in {
            HTTPStatus.BAD_REQUEST.value,
            HTTPStatus.UNPROCESSABLE_ENTITY.value,
        }

        if response.status_code == HTTPStatus.BAD_REQUEST.value:
            body = MessageErrorSchema.model_validate(response.json())
            assert body.message or body.detail

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("MFA: extra fields in request → 400 or 422")
    async def test_extra_fields_in_request(
        self,
        api_client,
        admin_credentials,
    ) -> None:
        response = await api_client.post(
            "/login",
            json={
                "orgName": admin_credentials["org_name"],
                "identity": admin_credentials["identity"],
                "password": admin_credentials["password"],
                "otp_code": "123456",
                "test": "extra_field",
            },
        )
        assert response.status_code in (
            HTTPStatus.BAD_REQUEST.value,
            HTTPStatus.UNPROCESSABLE_ENTITY.value,
        )

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("MFA: OTP with 7 digits (too long) → 400 or 422")
    async def test_otp_too_long(
        self,
        auth_client,
        admin_credentials,
    ) -> None:
        response = await auth_client.login(
            identity=admin_credentials["identity"],
            password=admin_credentials["password"],
            org_name=admin_credentials["org_name"],
            otp_code="1234567",
        )
        assert response.status_code in (
            HTTPStatus.BAD_REQUEST.value,
            HTTPStatus.UNPROCESSABLE_ENTITY.value,
        )

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("MFA: OTP with 5 digits (too short) → 400 or 422")
    async def test_otp_too_short(
        self,
        auth_client,
        admin_credentials,
    ) -> None:
        response = await auth_client.login(
            identity=admin_credentials["identity"],
            password=admin_credentials["password"],
            org_name=admin_credentials["org_name"],
            otp_code="12345",
        )
        assert response.status_code in (
            HTTPStatus.BAD_REQUEST.value,
            HTTPStatus.UNPROCESSABLE_ENTITY.value,
        )