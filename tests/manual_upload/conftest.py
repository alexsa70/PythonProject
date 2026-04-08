import os

import pytest
import pytest_asyncio

from src.clients.files_client import FilesClient
from src.clients.manual_loader_client import ManualLoaderClient
from src.helpers.files_helper import get_file_id_by_external_id
from src.schemas.manual_loader_schema import UploadManualFileResponseSchema


@pytest.fixture
def manual_loader_client(api_client):
    return ManualLoaderClient(api_client)


@pytest.fixture
def files_client(api_client):
    return FilesClient(api_client)


@pytest_asyncio.fixture
async def upload_file(manual_loader_client, files_client, admin_headers):
    uploaded_items: list[dict] = []

    async def _upload(file_path: str, folder_id: str | None = None) -> dict:
        upload_response = await manual_loader_client.upload_manual_file(
            headers=admin_headers,
            file_path=file_path,
            folder_id=folder_id,
        )
        assert upload_response.status_code == 200, (
            f"Upload failed. Status: {upload_response.status_code}. "
            f"Response: {upload_response.text}"
        )

        upload_body = UploadManualFileResponseSchema.model_validate(upload_response.json())

        file_id = await get_file_id_by_external_id(
            files_client,
            admin_headers,
            upload_body.external_id,
        )

        uploaded_file = {
            "file_id": file_id,
            "external_id": upload_body.external_id,
            "file_name": os.path.basename(file_path),
            "file_path": file_path,
        }

        uploaded_items.append(uploaded_file)
        return uploaded_file

    yield _upload

    for item in uploaded_items:
        delete_response = await manual_loader_client.delete_manual_files(
            headers=admin_headers,
            payload={"file_ids": [item["file_id"]]},
        )
        assert delete_response.status_code == 200, (
            f"Cleanup failed for file_id={item['file_id']}. "
            f"Response: {delete_response.text}"
        )