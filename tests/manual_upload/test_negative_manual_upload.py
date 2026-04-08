import os

import allure
import pytest

from tests.manual_upload.test_data.test_data import UNSUPPORTED_FILES


@pytest.mark.asyncio
@allure.feature("Manual Loader")
@allure.story("Unsupported file types")
@allure.severity(allure.severity_level.NORMAL)
class TestNegativeManualUpload:

    @pytest.mark.parametrize(
        "file_path",
        UNSUPPORTED_FILES,
        ids=lambda path: os.path.basename(path),
    )
    @allure.title("Manual upload: unsupported file type")
    async def test_upload_unsupported_file(
        self,
        manual_loader_client,
        admin_headers,
        file_path,
    ) -> None:
        with allure.step(f"Upload unsupported file: {file_path}"):
            response = await manual_loader_client.upload_manual_file(
                headers=admin_headers,
                file_path=file_path,
            )

        with allure.step("Verify response status code"):
            assert response.status_code in (400, 422)

        with allure.step("Verify error response contains message"):
            body = response.json()
            if isinstance(body, dict):
                assert body.get("message")