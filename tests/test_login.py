import json

import  httpx
import pytest
import allure


url = "https://kal-sense-bynet.kaleidoo-dev.com/login"
payload = {
  "identity": "Alex",
  "password": "2Fy9OL4%i?GBRn",
  "orgName": "QA"
}

@pytest.mark.asyncio
@allure.title("Login with valid credentials")
@allure.description("Verify that user can authenticate successfully and API returns 200")
async def test_login():
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        assert response.status_code == 200
        token = response.json()["token"]
        print(token)