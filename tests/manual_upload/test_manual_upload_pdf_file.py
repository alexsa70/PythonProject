import pytest
import allure


from src.clients.manual_loader_client import ManualLoaderClient
from src.schemas.manual_loader_schema import UploadManualFileResponseSchema
from src.utils.assertions import assert_status_code

@pytest.fixture
def manual_loader_client(api_client):
    return ManualLoaderClient(api_client)

VALID_PDF = "tests/manual_upload/test_files/test_file.pdf"

@pytest.mark.asyncio
@allure.feature("Manual Loader PDF")
@allure.severity(allure.severity_level.CRITICAL)
class TestManualUploadPDF:

    @allure.title("Upload valid PDF -> 200 OK")
    async def test_manual_upload_pdf(self,manual_loader_client, admin_headers) -> None:
        with allure.step("Upload valid PDF file"):
            response = await manual_loader_client.upload_manual_file(
                headers=admin_headers,
                file_path=VALID_PDF,
            )
            allure.attach(response.text, name="upload response", attachment_type=allure.attachment_type.JSON)
        with allure.step("Verify response code is 200"):
            assert_status_code(response, 200)
        with allure.step("Validate upload response schema"):
            body = UploadManualFileResponseSchema.model_validate(response.json())

        with allure.step("Verify upload response fields"):
            assert body.external_id
            assert body.message == "File uploaded successfully"
