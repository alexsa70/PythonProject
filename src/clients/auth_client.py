import httpx

from src.clients.api_client import ApiClient
from typing import Optional

class AuthClient:
    def __init__(self, api: ApiClient):
        self.api = api

    async def login(
            self,
            identity: str,
            password: str,
            org_name: str,
            otp_code: Optional[str] = None,
    ) -> httpx.Response:
        payload = {
            "identity": identity,
            "password": password,
            "orgName": org_name,
        }
        if otp_code is not None:
            payload["otp_code"] = otp_code
        return await self.api.post("/login", json=payload)