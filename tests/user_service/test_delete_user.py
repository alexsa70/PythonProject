import asyncio

import allure
import pytest

from src.clients.user_client import UserClient
from src.factories.user_factory import build_create_user_payload
from src.schemas.user_schema import (
    CreateUserResponseSchema,
    DeleteUserResponseSchema,
)
from src.utils.assertions import assert_status_code


@pytest.fixture
def users_client(api_client):
    return UserClient(api_client)


@pytest.mark.asyncio
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Admin can delete user")
async def test_admin_can_delete_user(
    users_client,
    admin_headers,
    admin_auth_context,
    role_ids,
    ui_debug_pause,
):
    with allure.step("Build create user payload"):
        create_payload = build_create_user_payload(
            org_name=admin_auth_context.org.org_name,
            role_id=role_ids["user"],
        )
        created_user_name = create_payload["user_name"]

    with allure.step("Create user for deletion"):
        create_response = await users_client.create_user(
            headers=admin_headers,
            payload=create_payload,
        )

    with allure.step("Verify create user status code is 200"):
        assert_status_code(create_response, 200)

    with allure.step("Validate create user response schema"):
        create_response_json = create_response.json()
        created_user = CreateUserResponseSchema.model_validate(create_response_json)

    with allure.step("Verify created user response fields"):
        assert created_user.message == "User created successfully"
        assert created_user.user_id

    with allure.step("Pause for UI debug if enabled"):
        await ui_debug_pause(
            f"Created user_id: {created_user.user_id}",
            seconds=20,
        )

    with allure.step("Send delete user request"):
        delete_response = await users_client.delete_user(
            headers=admin_headers,
            user_id=created_user.user_id,
        )

    with allure.step("Verify delete user status code is 200"):
        assert_status_code(delete_response, 200)

    with allure.step("Validate delete user response schema"):
        delete_response_json = delete_response.json()
        parsed_delete = DeleteUserResponseSchema.model_validate(delete_response_json)

    with allure.step("Verify delete user response fields"):
        assert parsed_delete.user_status == "On Hold"
        assert parsed_delete.message == "User deletion initiated and is being processed"

    with allure.step("Wait until user is deleted or becomes inactive"):
        user_deleted = await wait_until_user_deleted(
            users_client=users_client,
            headers=admin_headers,
            user_name=created_user_name,
            attempts=10,
            delay=2,
        )

    with allure.step("Verify user is no longer active/available"):
        assert user_deleted, (
            f"User '{created_user_name}' was still available after delete polling"
        )


async def wait_until_user_deleted(
    users_client: UserClient,
    headers: dict,
    user_name: str,
    attempts: int = 10,
    delay: int = 2,
) -> bool:
    for _ in range(attempts):
        response = await users_client.get_user(
            headers=headers,
            user_name=user_name,
        )

        if response.status_code in (400, 404):
            return True

        try:
            body = response.json()
        except ValueError:
            body = {}

        status = body.get("status")
        if status in ("On Hold", "Deleted", "Inactive"):
            return True

        await asyncio.sleep(delay)

    return False