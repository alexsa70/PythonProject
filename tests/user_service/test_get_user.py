import pytest
import allure

from src.clients.user_client import UserClient
from src.schemas.user_schema import UserResponseSchema, RolesResponseSchema
from src.utils.assertions import assert_status_code


@pytest.mark.asyncio
@pytest.mark.user_service
@allure.feature("User Service")
@allure.story("Get user")
class TestUserService:
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

    @allure.title("Users: retrieve all users")
    async def test_get_all_user(self, api_client, admin_headers, admin_auth_context):
        users_client = UserClient(api_client)

        response = await users_client.get_all_users(
            headers=admin_headers,

        )
        assert_status_code(response, 200)
        response_json = response.json()
        parsed_users = [UserResponseSchema.model_validate(user) for user in response_json]

        assert len(parsed_users) >= 1
        assert any(user.id == admin_auth_context.user.id for user in parsed_users)

    @allure.title("Users: get system roles")
    async def test_get_system_roles(self, api_client, admin_headers, admin_auth_context):
        users_client = UserClient(api_client)

        response = await users_client.get_system_roles(
            headers=admin_headers,

        )
        assert_status_code(response, 200)
        #response_json = response.json()
        parsed = RolesResponseSchema.model_validate(response.json())

        role_names = [role.name for role in parsed.root]

        assert "admin" in role_names
        assert "user" in role_names
        assert "super_admin" in role_names


