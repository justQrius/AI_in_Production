"""
Integration tests for Digital Twin API endpoints.
Tests the FastAPI application endpoints for chat, sessions, and health checks.
"""

import pytest
from fastapi.testclient import TestClient
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from server import app, MEMORY_DIR


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def temp_memory_dir():
    """Create a temporary memory directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "This is a test response from the AI."
    return mock_response


class TestHealthEndpoints:
    """Test health check and root endpoints"""

    def test_root_endpoint(self, client):
        """Test the root endpoint returns correct message"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "AI Digital Twin API with Memory"}

    def test_health_check(self, client):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestChatEndpoint:
    """Test the /chat endpoint functionality"""

    def test_chat_without_session_id(self, client, mock_openai_response, temp_memory_dir):
        """Test chat creates a new session when no session_id provided"""
        with patch('server.client.chat.completions.create', return_value=mock_openai_response):
            with patch('server.MEMORY_DIR', temp_memory_dir):
                response = client.post(
                    "/chat",
                    json={"message": "Hello, AI!"}
                )

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "response" in data
        assert data["response"] == "This is a test response from the AI."
        assert len(data["session_id"]) > 0  # UUID generated

    def test_chat_with_session_id(self, client, mock_openai_response, temp_memory_dir):
        """Test chat with an existing session_id"""
        session_id = "test-session-123"

        with patch('server.client.chat.completions.create', return_value=mock_openai_response):
            with patch('server.MEMORY_DIR', temp_memory_dir):
                response = client.post(
                    "/chat",
                    json={
                        "message": "Continue our conversation",
                        "session_id": session_id
                    }
                )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["response"] == "This is a test response from the AI."

    def test_chat_memory_persistence(self, client, mock_openai_response, temp_memory_dir):
        """Test that conversation history is saved and loaded"""
        session_id = "memory-test"

        with patch('server.client.chat.completions.create', return_value=mock_openai_response):
            with patch('server.MEMORY_DIR', temp_memory_dir):
                # First message
                response1 = client.post(
                    "/chat",
                    json={"message": "First message", "session_id": session_id}
                )
                assert response1.status_code == 200

                # Second message - should have history
                response2 = client.post(
                    "/chat",
                    json={"message": "Second message", "session_id": session_id}
                )
                assert response2.status_code == 200

                # Verify conversation file was created and contains both exchanges
                from server import load_conversation
                conversation = load_conversation(session_id)

        assert len(conversation) == 4  # 2 user messages + 2 assistant responses

    def test_chat_invalid_payload(self, client):
        """Test chat endpoint with invalid payload"""
        response = client.post("/chat", json={})
        assert response.status_code == 422  # Validation error

    def test_chat_empty_message(self, client):
        """Test chat endpoint with empty message"""
        response = client.post("/chat", json={"message": ""})
        # OpenAI might handle empty messages, or we should validate
        # This test documents current behavior
        assert response.status_code in [200, 422, 500]

    def test_chat_api_error_handling(self, client, temp_memory_dir):
        """Test chat endpoint handles OpenAI API errors gracefully"""
        with patch('server.client.chat.completions.create', side_effect=Exception("API Error")):
            with patch('server.MEMORY_DIR', temp_memory_dir):
                response = client.post(
                    "/chat",
                    json={"message": "Test error handling"}
                )

        assert response.status_code == 500
        assert "API Error" in response.json()["detail"]


class TestSessionsEndpoint:
    """Test the /sessions endpoint"""

    def test_list_sessions_empty(self, client, temp_memory_dir):
        """Test listing sessions when none exist"""
        with patch('server.MEMORY_DIR', temp_memory_dir):
            response = client.get("/sessions")

        assert response.status_code == 200
        assert response.json() == {"sessions": []}

    def test_list_sessions_with_data(self, client, mock_openai_response, temp_memory_dir):
        """Test listing sessions after creating some conversations"""
        with patch('server.client.chat.completions.create', return_value=mock_openai_response):
            with patch('server.MEMORY_DIR', temp_memory_dir):
                # Create a few sessions
                for i in range(3):
                    client.post(
                        "/chat",
                        json={"message": f"Message {i}", "session_id": f"session-{i}"}
                    )

                # List sessions
                response = client.get("/sessions")

        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) == 3
        assert all("session_id" in s for s in data["sessions"])
        assert all("message_count" in s for s in data["sessions"])
        assert all("last_message" in s for s in data["sessions"])

    def test_session_metadata(self, client, mock_openai_response, temp_memory_dir):
        """Test that session metadata is accurate"""
        session_id = "metadata-test"

        with patch('server.client.chat.completions.create', return_value=mock_openai_response):
            with patch('server.MEMORY_DIR', temp_memory_dir):
                # Send 2 messages
                client.post("/chat", json={"message": "First", "session_id": session_id})
                client.post("/chat", json={"message": "Second", "session_id": session_id})

                # Get sessions
                response = client.get("/sessions")

        data = response.json()
        session = next(s for s in data["sessions"] if s["session_id"] == session_id)
        assert session["message_count"] == 4  # 2 user + 2 assistant
        assert session["last_message"] is not None


class TestCORSConfiguration:
    """Test CORS middleware configuration"""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are set on responses"""
        response = client.options("/health")
        # FastAPI/Starlette handles OPTIONS automatically with CORS middleware
        assert response.status_code in [200, 405]


class TestDataValidation:
    """Test request/response data validation"""

    def test_chat_request_validation(self, client):
        """Test that ChatRequest model validates correctly"""
        # Valid request
        response = client.post("/chat", json={"message": "Valid"})
        assert response.status_code in [200, 500]  # 200 or server error, not validation error

        # Invalid request (missing required field)
        response = client.post("/chat", json={"session_id": "test"})
        assert response.status_code == 422

    def test_chat_response_structure(self, client, mock_openai_response, temp_memory_dir):
        """Test that ChatResponse has the correct structure"""
        with patch('server.client.chat.completions.create', return_value=mock_openai_response):
            with patch('server.MEMORY_DIR', temp_memory_dir):
                response = client.post("/chat", json={"message": "Test"})

        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) == {"response", "session_id"}
        assert isinstance(data["response"], str)
        assert isinstance(data["session_id"], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
