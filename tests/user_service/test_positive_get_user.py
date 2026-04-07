import pytest
import allure

from src.clients.user_client import UserClient
from src.schemas.user_schema import UserResponseSchema, RolesResponseSchema, UserUpdateResponseSchema
from src.utils.assertions import assert_status_code
from src.factories.user_factory import fake

@pytest.fixture
def users_client(api_client):
    return UserClient(api_client)


@pytest.mark.asyncio
@pytest.mark.user_service
@allure.feature("User Service")
@allure.story("Positive tests for user service")
class TestPositiveUserService:
    @allure.title("Users: retrieve user by name")
    @allure.severity(allure.severity_level.CRITICAL)
    async def test_get_user_by_name(self, api_client,admin_headers, admin_auth_context, users_client):
        with allure.step("Send POST /user?name=... request"):
            response = await users_client.get_user(
                headers=admin_headers,
                user_name=admin_auth_context.user.user_name,
                )
        with allure.step("Assert status code is 200"):
            assert_status_code(response, 200)
        with allure.step("Validate response schema and user_name"):
            response_json = response.json()
            parsed = UserResponseSchema.model_validate(response_json)
            assert parsed.user_name == admin_auth_context.user.user_name

    @allure.title("Users: retrieve user by id")
    @allure.severity(allure.severity_level.CRITICAL)
    async def test_get_user_by_id(self, api_client,admin_headers, admin_auth_context, users_client):
        with allure.step("Send POST /user?id=... request"):
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
    @allure.severity(allure.severity_level.NORMAL)
    async def test_get_all_user(self, api_client, admin_headers, admin_auth_context, users_client):
        with allure.step("Send POST /all_users... request"):
             response = await users_client.get_all_users(
                 headers=admin_headers,
                 )
        assert_status_code(response, 200)
        response_json = response.json()
        parsed_users = [UserResponseSchema.model_validate(user) for user in response_json]

        assert len(parsed_users) >= 1
        #assert any(user.id == admin_auth_context.user.id for user in parsed_users)
        assert all(isinstance(user.id, str) for user in parsed_users)

    @pytest.mark.parametrize("role_name", ["admin", "user", "super_admin"])
    @allure.title("Users: get system roles contains {role_name}")
    @allure.severity(allure.severity_level.MINOR)
    async def test_get_system_roles(self, api_client, admin_headers, admin_auth_context, users_client, role_name):
        with allure.step("Send POST /system_roles... request"):
            response = await users_client.get_system_roles(headers=admin_headers,)
        assert_status_code(response, 200)
        parsed = RolesResponseSchema.model_validate(response.json())

        role_names = [role.name for role in parsed.root]
        assert role_name in role_names

    @pytest.mark.asyncio
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("User: update current admin user")
    async def test_user_update(
            self,
            users_client,
            admin_headers,
            admin_auth_context,
    ) -> None:
        current_user_id = admin_auth_context.user.id


        with allure.step("Get current user before update"):
            before_response = await users_client.get_user_by_id(
                headers=admin_headers,
                user_id=current_user_id,
            )
            assert_status_code(before_response, 200)

            before_user = UserResponseSchema.model_validate(before_response.json())
            original_last_name = before_user.last_name

        new_last_name = f"QA{fake.first_name()}"

        with allure.step("Update current user last name"):
            update_payload = {
                "user_id": current_user_id,
                "last_name": new_last_name,
            }

            response = await users_client.update_user(
                headers=admin_headers,
                payload=update_payload,
            )
            assert_status_code(response, 200)

            body = UserUpdateResponseSchema.model_validate(response.json())
            assert body.message == "User updated successfully"

        try:
            with allure.step("Verify user was updated"):
                get_by_id_response = await users_client.get_user_by_id(
                    headers=admin_headers,
                    user_id=current_user_id,
                )
                assert_status_code(get_by_id_response, 200)

                updated_user = UserResponseSchema.model_validate(get_by_id_response.json())
                assert updated_user.last_name == new_last_name

        finally:
            with allure.step("Rollback user last name to original value"):
                rollback_payload = {
                    "user_id": current_user_id,
                    "last_name": original_last_name,
                }

                rollback_response = await users_client.update_user(
                    headers=admin_headers,
                    payload=rollback_payload,
                )
                assert_status_code(rollback_response, 200)


