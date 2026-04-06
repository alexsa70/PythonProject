from pydantic import BaseModel, EmailStr, RootModel
from datetime import datetime

class UserResponseSchema(BaseModel):
    id: str
    user_name: str
    email: EmailStr
    first_name: str
    last_name: str
    user_type: str
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    created_by: str | None = None

    model_config = {
        "extra": "allow"
    }

class CreateUserResponseSchema(BaseModel):
    message: str
    user_id: str

    model_config = {
        "extra": "allow"}


class DeleteUserResponseSchema(BaseModel):
    message: str
    user_status: str

    model_config = {
        "extra": "allow"
    }

class UsersListResponseSchema(BaseModel):
    users: list[UserResponseSchema]
    total_count: int

    model_config = {
        "extra": "allow"
    }

# =========================
# Roles schemas
# =========================

class RoleSchema(BaseModel):
    id: str
    name: str
    description: str

    model_config = {
        "extra": "allow"
    }


class RolesResponseSchema(RootModel[list[RoleSchema]]):
    pass