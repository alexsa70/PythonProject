import pytest
import allure

from src.clients.user_client import UserClient
from src.schemas.user_schema import UserResponseSchema
from src.utils.assertions import assert_status_code


@pytest.mark.asyncio
@pytest.mark.user_service
@allure.feature("User Service")
class TestUserService:
    @allure.story("Get user")
    @allure.title("Users: retrieve user by name")
    async def test_get_user_by_name(self, api_client,admin_headers, admin_auth_context):
        users_client = UserClient(api_client)

        response = await users_client.get_user(
            headers=admin_headers,
            user_name=admin_auth_context.user.user_name,
            )

        assert_status_code(response, 200)

        response_json = response.json()
        parsed = UserResponseSchema.model_validate(response_json)
        assert parsed.user_name == admin_auth_context.user.user_name

    @allure.story("Get user")
    @allure.title("Users: retrieve user by id")
    async def test_get_user_by_id(self, api_client,admin_headers, admin_auth_context):
        users_client = UserClient(api_client)

        response = await users_client.get_user_by_id(
            headers=admin_headers,
            user_id=admin_auth_context.user.id,
        )
        assert_status_code(response, 200)
        response_json = response.json()
        parsed = UserResponseSchema.model_validate(response_json)
        assert parsed.id == admin_auth_context.user.id
        assert parsed.user_name == admin_auth_context.user.user_name


