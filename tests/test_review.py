# Test file for review endpoints
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services import openai_integration


@pytest.fixture(autouse=True)
def mock_generate_code_review(monkeypatch):
    async def dummy_review(code: str) -> str:
        return "Looks good!"
    monkeypatch.setattr(openai_integration, "generate_code_review", dummy_review)

client = TestClient(app)

def test_review_endpoint():
    # Sample payload data
    payload = {
        "repository": "my-repo",
        "pr_number": 123,
        "code": "def foo():\n    return 'bar'"
    }
    #  Make a POST request to the review endpoint
    response = client.post("/api/review/", json=payload)

    # Check that the response status code is 200 (OK)
    assert response.status_code == 200,  f"Expected status code 200, got {response.status_code}"

    # Check that the response JSON contains a 'review' key
    data = response.json()
    assert "review" in data, "Response JSON should contain a key 'review'"

    assert data["review"] == "Looks good!"

