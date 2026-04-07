import pytest
import pytest_asyncio

from src.config import settings
from src.factories.user_factory import build_create_user_payload
from src.schemas.user_schema import CreateUserResponseSchema

@pytest.fixture(scope="session")
def admin_org() -> str:
    if not settings.admin_org:
        pytest.skip("No admin org defined")
    return settings.admin_org

@pytest.fixture(scope="session")
def role_ids() -> dict:
    return {
        "super_admin": "699180f94eb0d6e84a84998d",
        "admin": "699180f94eb0d6e84a84998e",
        "user": "699180f94eb0d6e84a84998f",
    }
# =========================
# Temporary user fixture
# =========================

@pytest_asyncio.fixture
async def temporary_user(users_client, admin_headers,admin_auth_context, role_ids):
    payload = build_create_user_payload(
        org_name=admin_auth_context.org.org_name,
        role_id=role_ids["user"],
    )
    create_response = await users_client.create_user(
        headers=admin_headers,
        payload=payload,
    )
    assert create_response.status_code == 200, (
        f"Create user failed. Status: {create_response.status_code}."
        f"Response: {create_response.text}"
    )
    parsed = CreateUserResponseSchema.model_validate(create_response.json())

    user_data = {
        "user_id": parsed.user_id,
        "user_name": payload["user_name"],
        "email": payload["email"],
        "org_name": payload["org_name"],
    }
    yield user_data

    #cleanup
    delete_response = await users_client.delete_user(
        headers=admin_headers,
        user_id=user_data["user_id"],
    )
    assert delete_response.status_code == 200, (
        f"Delete user cleanup failed. Status: {delete_response.status_code}."
        f"Response: {delete_response.text}"
    )