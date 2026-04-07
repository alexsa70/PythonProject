import httpx

from src.clients.api_client import ApiClient
from typing import Optional

class AuthClient:
    def __init__(self, api: ApiClient):
        self.api = api

    # Login
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

    # SSO Login
    async def sso_login(
            self,
            org_name: str,
            redirect_uri: str,
            provider: str,
            code: str,
            code_verifier: Optional[str] = None,
    ) -> httpx.Response:
        payload = {
            "orgName": org_name,
            "redirect_uri": redirect_uri,
            "provider": provider,
            "code": code,
        }
        if code_verifier is not None:
            payload["code_verifier"] = code_verifier
        return await self.api.post("/sso_login", json=payload)