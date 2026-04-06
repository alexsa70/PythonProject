import pytest

from src.config import settings

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
