import os

import allure
import pytest

from src.schemas.files_schema import FilesListResponseSchema
from src.utils.assertions import assert_status_code
from tests.manual_upload.test_data.test_data import SUPPORTED_FILES


@pytest.mark.asyncio
@allure.feature("Manual Loader")
@allure.story("Uploaded file metadata")
@allure.severity(allure.severity_level.NORMAL)
class TestUploadedFileMetadata:

    @pytest.mark.parametrize(
        "file_case",
        SUPPORTED_FILES,
        ids=lambda case: os.path.basename(case["path"]),
    )
    @allure.title("Uploaded file is present in Files service")
    async def test_uploaded_file_present_in_files_service(
        self,
        upload_file,
        files_client,
        admin_headers,
        file_case,
    ) -> None:
        with allure.step(f"Upload file: {file_case['path']}"):
            uploaded = await upload_file(file_case["path"])

        with allure.step("Get files list"):
            response = await files_client.get_files(headers=admin_headers)
            assert_status_code(response, 200)

        with allure.step("Find uploaded file in files list"):
            parsed = FilesListResponseSchema.model_validate(response.json())
            matched_file = next(
                (file for file in parsed.files if file.id == uploaded["file_id"]),
                None,
            )

            assert matched_file is not None
            assert matched_file.external_id == uploaded["external_id"]
            assert matched_file.name == uploaded["file_name"]