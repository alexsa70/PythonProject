
import httpx

from src.clients.api_client import ApiClient


class UserClient:
    def __init__(self, api: ApiClient) -> None:
        self.api = api

    async def get_user(self, headers: dict, user_name: str) -> httpx.Response:
        payload = {
            "user_name": user_name,
        }
        return await self.api.post(
            "/api/user/get",
            json=payload,
            headers=headers
        )
    async def create_user(self, headers: dict, payload: dict) -> httpx.Response:
        files = {
            key: (None, str(value).lower() if isinstance(value, bool) else str(value))
            for key, value in payload.items()
        }
        return await self.api.post(
            "/api/user/create",
            files=files,
            headers=headers
        )
    async def delete_user(self, headers: dict, user_id: str) -> httpx.Response:
        payload = {
            "user_id": user_id,
            }
        return await self.api.post(
            "/api/user/delete",
            json=payload,
            headers=headers
        )
    async def get_user_by_id(self, headers: dict, user_id: str) -> httpx.Response:
        payload = {
            "user_id": user_id,
        }
        return await self.api.post(
            "/api/user/get_by_id",
            json=payload,
            headers=headers
        )