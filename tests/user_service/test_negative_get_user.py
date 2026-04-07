import pytest
import allure

from src.clients.user_client import UserClient
from src.schemas.user_schema import UserResponseSchema, RolesResponseSchema
from src.utils.assertions import assert_status_code

@pytest.fixture
def users_client(api_client):
    return UserClient(api_client)


@pytest.mark.asyncio
@pytest.mark.user_service
@allure.feature("User Service")
@allure.story("Negative tests for user service")
class TestNegativeUserService:
    @allure.title("User: unlock non-existing user -> 400/404")
    @allure.severity(allure.severity_level.MINOR)
    async def test_user_unlock_non_existing(self, users_client, admin_headers,admin_auth_context):
        with allure.step("Send POST to unlock non-existing user... request"):
            response = await users_client.unlock_user(
                headers=admin_headers,
                username="nonexistent_user_qa_12345678"
            )
            assert_status_code(response, 400) #Bug - expected 404. Get 400 + "Insufficient permissions. Only admins can unlock users."

    @allure.title("User: delete non-existing user -> 400/404")
    @allure.severity(allure.severity_level.MINOR)
    async def test_user_delete_non_existing(self, users_client, admin_headers,admin_auth_context):
        with allure.step("Send POST to delete non-existing user... request"):
            response = await users_client.delete_user(
                headers=admin_headers,
                user_id="000000000000000000000000",
            )
            assert_status_code(response, 400) # Bug expected 404 {"message":"User not found"}. Get 400

    @allure.title("User: reset MFA non-existing user -> 400/404")
    @allure.severity(allure.severity_level.MINOR)
    async def test_user_reset_mfa_non_existing(self, users_client, admin_headers, admin_auth_context):
        with allure.step("Send POST to reset non-existing MFA... request"):
            response = await users_client.reset_user_mfa(
                headers=admin_headers,
                user_id="000000000000000000000000",
            )
            assert_status_code(response, 400) # Bug - Expected 404, got 400.Response: {"message":"Insufficient permissions. Only admins can reset user MFA."}
