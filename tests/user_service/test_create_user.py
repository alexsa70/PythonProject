import pytest
import allure



from src.clients.user_client import UserClient
from src.utils.assertions import assert_status_code
from src.schemas.user_schema import CreateUserResponseSchema
from src.factories.user_factory import build_create_user_payload


@pytest.fixture
def users_client(api_client):
    return UserClient(api_client)

@pytest.mark.asyncio
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Admin can create user")
@allure.testcase("Admin can create regular user")
async def test_admin_can_create_regular_user(users_client, admin_headers, admin_auth_context, role_ids):
    with allure.step("Build create user payload"):
        payload = build_create_user_payload(
            org_name=admin_auth_context.org.org_name,
            role_id=role_ids["user"]
            )
    with allure.step("Send create user request"):
        response = await users_client.create_user(
            headers=admin_headers,
            payload = payload
           )
    assert_status_code(response, 200)

    response_json = response.json()
    parsed = CreateUserResponseSchema.model_validate(response_json)

    assert parsed.message == "User created successfully"
    assert parsed.user_id

    with allure.step("Cleanup created user"):
        delete_response = await users_client.delete_user(
            headers=admin_headers,
            user_id= parsed.user_id,
        )
        assert_status_code(delete_response, 200)