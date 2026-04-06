from faker import Faker

fake = Faker()

def build_create_user_payload(org_name: str, role_id: str) -> dict:
    username = f"{fake.user_name()}_qa"
    return {
        "org_name": org_name,
        "user_name": username,
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "role_id": role_id,
        "email": fake.unique.email(),
        "is_ldap_sso_user": False,
    }