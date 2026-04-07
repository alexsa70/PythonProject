import mimetypes
from pathlib import Path
from typing import Optional

import httpx

from src.clients.api_client import ApiClient


class ManualLoaderClient:
    def __init__(self, api: ApiClient) -> None:
        self.api = api

    # ==========================
    # Upload file
    # ==========================
    async def upload_manual_file(
        self,
        headers: dict,
        file_path: str,
        content_type: Optional[str] = None,
        folder_id: Optional[str] = None,
    ) -> httpx.Response:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        resolved_content_type = (
            content_type
            or mimetypes.guess_type(path.name)[0]
            or "application/octet-stream"
        )

        files = {
            "file": (path.name, path.read_bytes(), resolved_content_type)
        }

        data = {}
        if folder_id:
            data["folder_id"] = folder_id

        return await self.api.post(
            "/api/manual_loader/upload_manual_file",
            headers=headers,
            files=files,
            data=data if data else None,
        )

    # ==========================
    # Delete files
    # ==========================
    async def delete_manual_files(
        self,
        headers: dict,
        payload: dict,
    ) -> httpx.Response:
        """
        payload example:
        {
            "external_ids": ["EXT123", "EXT456"]
        }
        """

        return await self.api.post(
            "/api/manual_loader/delete_manual_files",
            headers=headers,
            json=payload,
        )