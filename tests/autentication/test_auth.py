import pytest
import allure

from src.utils.assertions import assert_status_code

@pytest.mark.asyncio
@allure.title("Login with valid credentials")
async def test_login(auth_client, user_credentials):
    response = await auth_client.login(
        identity=user_credentials["identity"],
        password=user_credentials["password"],
        org_name=user_credentials["org_name"],
    )
    assert_status_code(response, 200)
    response_json = response.json()
    print(response_json)