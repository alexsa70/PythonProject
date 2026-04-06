import pytest
import allure



from src.clients.user_client import UserClient
from src.utils.assertions import assert_status_code
from src.schemas.user_schema import CreateUserResponseSchema
from src.factories.user_factory import build_create_user_payload



@pytest.mark.asyncio
@allure.title("Admin can create user")
@allure.testcase("Admin can create regular user")
async def test_admin_can_create_regular_user(api_client, admin_headers, admin_org, role_ids):
    user_client = UserClient(api_client)

    payload = build_create_user_payload(
        org_name=admin_org,
        role_id=role_ids["user"]
    )
    response = await user_client.create_user(
        headers=admin_headers,
        payload = payload
    )
    assert_status_code(response, 200)

    response_json = response.json()
    parsed = CreateUserResponseSchema.model_validate(response_json)

    assert parsed.message == "User created successfully"
    assert parsed.user_id