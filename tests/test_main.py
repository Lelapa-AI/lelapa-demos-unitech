# test_main.py

import os
import pytest
from fastapi.testclient import TestClient
from main import app  # Assuming your FastAPI app is in `main.py`

# Set up the test client
client = TestClient(app)

@pytest.fixture
def setup_environment():
    # Set environment variables for testing
    os.environ["VULAVULA_API_TOKEN"] = "test_token"
    os.environ["ESKOM_FAQ_FILE_PATH"] = "test_eskom_faq.json"
    os.environ["EMFULENI_FAQ_FILE_PATH"] = "test_emfuleni_faq.json"
    yield
    # Clean up after tests if needed

def test_root(setup_environment):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Emfuleni FAQ API"}

def test_answer_question_success(setup_environment):
    # Assuming you have a valid setup for the FAQ files and a mock response
    response = client.post("/faq", json={"question": "What is Eskom?", "language": "eng_Latn"})
    assert response.status_code == 200
    assert "answer" in response.json()

def test_answer_question_failure(setup_environment):
    # Simulate a scenario where the API should fail
    response = client.post("/faq", json={"question": "Unknown question"})
    assert response.status_code == 500
    assert "detail" in response.json()
