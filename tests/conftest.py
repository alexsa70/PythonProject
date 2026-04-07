import pytest
import pytest_asyncio
import asyncio
from typing import Any

from src.clients.api_client import ApiClient
from src.clients.auth_client import AuthClient
from src.config import settings
from src.utils.debug import debug_pause
from src.schemas.auth_schema import AuthResponseSchema

_auth_context_cache: dict[str, AuthResponseSchema] = {}
_auth_context_lock = asyncio.Lock()

def _build_credentials(
        identity: str | None,
        password: str | None,
        org_name: str | None,
        role_name: str,
) -> dict:
    if not all([identity, password, org_name]):
        pytest.skip(f"{role_name} credentials not provided in .env")
    return {
        "identity": identity,
        "password": password,
        "org_name": org_name,
    }

# def _extract_token(response_json: dict[str, Any]) -> str:
#     token = response_json.get("token")
#
#     assert isinstance(token, str),(
#         f"Token not found in response: {response_json}"
#     )
#     return token

@pytest_asyncio.fixture
async def api_client():
    async with ApiClient(base_url=settings.base_url) as client:
        yield client

@pytest_asyncio.fixture
async def auth_client(api_client) -> AuthClient:
    return AuthClient(api_client)

@pytest_asyncio.fixture(scope="session")
def admin_credentials() -> dict:
    return _build_credentials(
        identity=settings.admin_identity,
        password=settings.admin_password,
        org_name=settings.admin_org,
        role_name="Admin",
    )
@pytest_asyncio.fixture(scope="session")
def user_credentials() -> dict:
    return _build_credentials(
        identity=settings.user_identity,
        password=settings.user_password,
        org_name=settings.user_org,
        role_name="User",
    )
@pytest.fixture(scope="session")
def super_admin_credentials() -> dict:
    return _build_credentials(
        identity=settings.super_admin_identity,
        password=settings.super_admin_password,
        org_name=settings.super_admin_org,
        role_name="Super admin",
    )
async def _get_or_create_auth_context(
    role_name: str,
    auth_client: AuthClient,
    credentials: dict,
) -> AuthResponseSchema:
    if role_name in _auth_context_cache:
        return _auth_context_cache[role_name]

    async with _auth_context_lock:
        if role_name in _auth_context_cache:
            return _auth_context_cache[role_name]

        response = await auth_client.login(**credentials)
        assert response.status_code == 200, (
            f"{role_name} login failed. Status: {response.status_code}. "
            f"Response: {response.text}"
        )

        context = AuthResponseSchema.model_validate(response.json())
        _auth_context_cache[role_name] = context
        return context

@pytest_asyncio.fixture
async def admin_auth_context(auth_client, admin_credentials) -> AuthResponseSchema:
    return await _get_or_create_auth_context("admin", auth_client, admin_credentials)


@pytest_asyncio.fixture
async def user_auth_context(auth_client, user_credentials) -> AuthResponseSchema:
    return await _get_or_create_auth_context("user", auth_client, user_credentials)


@pytest_asyncio.fixture
async def super_admin_auth_context(
    auth_client,
    super_admin_credentials,
) -> AuthResponseSchema:
    return await _get_or_create_auth_context(
        "super_admin",
        auth_client,
        super_admin_credentials,
    )

# @pytest_asyncio.fixture
# async def admin_auth_context(auth_client, admin_credentials) -> AuthResponseSchema:
#     response = await auth_client.login(**admin_credentials)
#     assert response.status_code == 200, (
#         f"Admin login failed. Status: {response.status_code}. "
#         f"Response: {response.text}"
#     )
#     return AuthResponseSchema.model_validate(response.json())
#
# @pytest_asyncio.fixture
# async def user_auth_context(auth_client, user_credentials) -> AuthResponseSchema:
#     response = await auth_client.login(**user_credentials)
#     assert response.status_code == 200, (
#         f"User login failed. Status: {response.status_code}. "
#         f"Response: {response.text}"
#     )
#     return AuthResponseSchema.model_validate(response.json())
#
# @pytest_asyncio.fixture
# async def super_admin_auth_context(auth_client, super_admin_credentials) -> AuthResponseSchema:
#     response = await auth_client.login(**super_admin_credentials)
#     assert response.status_code == 200, (
#         f"Super admin login failed. Status: {response.status_code}. "
#         f"Response: {response.text}"
#     )
#     return AuthResponseSchema.model_validate(response.json())

@pytest.fixture
def admin_token(admin_auth_context) -> str:
    return admin_auth_context.token

@pytest.fixture
def user_token(user_auth_context) -> str:
    return user_auth_context.token

@pytest.fixture
def super_admin_token(super_admin_auth_context) -> str:
    return super_admin_auth_context.token



# @pytest_asyncio.fixture
# async def admin_token(auth_client, admin_credentials) -> str:
#     response = await auth_client.login(**admin_credentials)
#     assert response.status_code == 200, (
#         f"Admin login failed. Status: {response.status_code}. "
#         f"Response: {response.text}"
#     )
#     return _extract_token(response.json())

# @pytest_asyncio.fixture
# async def user_token(auth_client, user_credentials) -> str:
#     response = await auth_client.login(**user_credentials)
#     assert response.status_code == 200, (
#         f"User login failed. Status: {response.status_code}. "
#         f"Response: {response.text}"
#     )
#     return _extract_token(response.json())
#
# @pytest_asyncio.fixture
# async def super_admin_token(auth_client, super_admin_credentials) -> str:
#     response = await auth_client.login(**super_admin_credentials)
#     assert response.status_code == 200, (
#         f"Super admin login failed. Status: {response.status_code}. "
#         f"Response: {response.text}"
#     )
#     return _extract_token(response.json())

@pytest.fixture
def admin_headers(admin_token) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def user_headers(user_token) -> dict:
    return {"Authorization": f"Bearer {user_token}"}

@pytest.fixture
def super_admin_headers(super_admin_token) -> dict:
    return {"Authorization": f"Bearer {super_admin_token}"}
# Debug tools
@pytest_asyncio.fixture
async def ui_debug_pause():
    async def _pause(message: str, seconds: int = 20) -> None:
        await debug_pause(message, seconds)
    return _pause