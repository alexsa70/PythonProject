import os

import allure
import pytest

from tests.manual_upload.test_data.test_data import SUPPORTED_FILES


@pytest.mark.asyncio
@allure.feature("Manual Loader")
@allure.story("Supported file types")
@allure.severity(allure.severity_level.CRITICAL)
class TestPositiveManualUpload:

    @pytest.mark.parametrize(
        "file_case",
        SUPPORTED_FILES,
        ids=lambda case: os.path.basename(case["path"]),
    )
    @allure.title("Manual upload: supported file type")
    async def test_upload_supported_file(
        self,
        upload_file,
        file_case,
    ) -> None:
        with allure.step(f"Upload supported file: {file_case['path']}"):
            uploaded = await upload_file(file_case["path"])

        with allure.step("Verify uploaded file ids exist"):
            assert uploaded["external_id"]
            assert uploaded["file_id"]