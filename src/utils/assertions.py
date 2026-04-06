import httpx
import allure

def assert_status_code(response: httpx.Response, expected_status: int) -> None:
    if response.status_code != expected_status:
        allure.attach(
            response.text,
            name="response_body",
            attachment_type=allure.attachment_type.JSON,
        )
    assert  response.status_code ==expected_status,(
        f"Expected {expected_status}, got {response.status_code}."
        f"Response: {response.text}"
)