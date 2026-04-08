import httpx

from src.clients.api_client import ApiClient

# Files Service client

class FilesClient:
    def __init__(self, api: ApiClient) -> None:
        self.api = api

    async def get_files(self, headers: dict, payload: dict | None = None) -> httpx.Response:
        return await self.api.post(
            "/api/files/get_files",
            headers=headers,
            json=payload or {},
        )