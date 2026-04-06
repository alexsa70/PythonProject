import pytest
import allure

from src.clients.user_client import UserClient
from src.schemas.user_schema import UserResponseSchema
from src.utils.assertions import assert_status_code


@pytest.mark.asyncio
@allure.title("Get users with valid admin token")
async def test_get_user(api_client,admin_headers):
    users_client = UserClient(api_client)

    response = await users_client.get_user(
        headers=admin_headers,
        user_name="Alex",
        )

    assert_status_code(response, 200)

    response_json = response.json()
    parsed = UserResponseSchema.model_validate(response_json)
    assert parsed.user_name == "Alex"
