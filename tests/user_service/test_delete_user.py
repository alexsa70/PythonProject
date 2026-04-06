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



@pytest.mark.asyncio
@allure.title("Admin can delete user")
async def test_admin_can_delete_user(
    api_client,
    admin_headers,
    admin_org,
    role_ids,
    ui_debug_pause,
):
    user_client = UserClient(api_client)

    create_payload = build_create_user_payload(
        org_name=admin_org,
        role_id=role_ids["user"],
    )
    created_user_name = create_payload["user_name"]

    create_response = await user_client.create_user(
        headers=admin_headers,
        payload=create_payload,
    )
    assert_status_code(create_response, 200)

    create_response_json = create_response.json()
    created_user = CreateUserResponseSchema.model_validate(create_response_json)

    assert created_user.message == "User created successfully"
    assert created_user.user_id

    await ui_debug_pause(
        f"Created user_id: {created_user.user_id}",
        seconds=20
    )

    delete_response = await user_client.delete_user(
        headers=admin_headers,
        user_id=created_user.user_id,
    )
    assert_status_code(delete_response, 200)

    delete_response_json = delete_response.json()
    parsed_delete = DeleteUserResponseSchema.model_validate(delete_response_json)

    assert parsed_delete.user_status == "On Hold"
    assert parsed_delete.message == "User deletion initiated and is being processed"

    user_deleted = await wait_until_user_deleted(
        user_client=user_client,
        headers=admin_headers,
        user_name=created_user_name,
        attempts=10,
        delay=2,
    )

    assert user_deleted, (
        f"User '{created_user_name}' was still available after delete polling"
    )


async def wait_until_user_deleted(
    user_client: UserClient,
    headers: dict,
    user_name: str,
    attempts: int = 10,
    delay: int = 2,
) -> bool:
    for _ in range(attempts):
        response = await user_client.get_user(
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