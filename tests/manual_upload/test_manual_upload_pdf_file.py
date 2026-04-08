import pytest
import allure


from src.clients.manual_loader_client import ManualLoaderClient
from src.schemas.manual_loader_schema import UploadManualFileResponseSchema
from src.clients.files_client import FilesClient
from src.utils.assertions import assert_status_code
from src.helpers.files_helper import get_file_id_by_external_id



@pytest.fixture
def manual_loader_client(api_client):
    return ManualLoaderClient(api_client)

@pytest.fixture
def files_client(api_client):
    return FilesClient(api_client)

VALID_PDF = "tests/manual_upload/test_files/test_file.pdf"

@pytest.mark.asyncio
@allure.feature("Manual Loader PDF")
@allure.story("Upload -> Verify in Files -> Delete")
@allure.severity(allure.severity_level.CRITICAL)
class TestManualUploadPDF:

    @allure.title("Upload valid PDF -> 200 OK")
    @allure.description("""
    This test verifies the full lifecycle of a manually uploaded PDF:
    1. Upload file via Manual Loader
    2. Verify file appears in Files service
    3. Delete uploaded file
    """)
    async def test_manual_upload_pdf(self,manual_loader_client, files_client, admin_headers) -> None:
        with allure.step("Step 1: Upload valid PDF file"):
            response = await manual_loader_client.upload_manual_file(
                headers=admin_headers,
                file_path=VALID_PDF,
            )
            allure.attach(response.text, name="upload response", attachment_type=allure.attachment_type.JSON)

        with allure.step("Step 2: Verify upload response is successfully"):
            assert_status_code(response, 200)
        with allure.step("Validate upload response schema"):
            body = UploadManualFileResponseSchema.model_validate(response.json())

        with allure.step("Verify upload response fields"):
            assert body.external_id
            assert body.message == "File uploaded successfully"

        external_id = body.external_id

        with allure.step("Step 3: Resolve internal file id via Files service"):
            file_id = await get_file_id_by_external_id(
                files_client,
                admin_headers,
                external_id)

        with allure.step("Step 4: Delete file by internal id"):
            delete_response = await manual_loader_client.delete_manual_files(
                headers=admin_headers,
                payload={"file_ids": [file_id]}
            )
        with allure.step("Step 5: Verify delete response is successful"):
            assert_status_code(delete_response, 200)
            allure.attach(delete_response.text, name="delete response", attachment_type=allure.attachment_type.JSON)
