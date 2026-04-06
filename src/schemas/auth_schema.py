from pydantic import BaseModel, EmailStr


class AuthUserSchema(BaseModel):
    id: str
    org_id: str
    user_name: str
    first_name: str
    last_name: str
    role_id: str
    email: EmailStr
    status: str
    user_type: str

    model_config = {
        "extra": "allow"
    }


class AuthOrgSchema(BaseModel):
    id: str
    org_name: str
    admin_email: EmailStr | None = None
    default_language: str | None = None

    model_config = {
        "extra": "allow"
    }


class AuthResponseSchema(BaseModel):
    token: str
    refresh_token: str | None = None
    expires_in: int | None = None
    user: AuthUserSchema
    org: AuthOrgSchema

    model_config = {
        "extra": "allow"
    }