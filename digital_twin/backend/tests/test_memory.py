"""
Unit tests for memory functions in the Digital Twin backend.
Tests conversation storage, retrieval, and session management.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from server import load_conversation, save_conversation, load_personality


class TestMemoryFunctions:
    """Test suite for memory management functions"""

    @pytest.fixture
    def temp_memory_dir(self):
        """Create a temporary memory directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_save_and_load_conversation(self, temp_memory_dir):
        """Test saving and loading a conversation"""
        session_id = "test-session-123"
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]

        # Patch the MEMORY_DIR
        with patch('server.MEMORY_DIR', temp_memory_dir):
            save_conversation(session_id, messages)
            loaded_messages = load_conversation(session_id)

        assert loaded_messages == messages
        assert len(loaded_messages) == 2
        assert loaded_messages[0]["role"] == "user"
        assert loaded_messages[1]["role"] == "assistant"

    def test_load_nonexistent_conversation(self, temp_memory_dir):
        """Test loading a conversation that doesn't exist"""
        with patch('server.MEMORY_DIR', temp_memory_dir):
            messages = load_conversation("nonexistent-session")

        assert messages == []

    def test_save_conversation_creates_file(self, temp_memory_dir):
        """Test that save_conversation creates a JSON file"""
        session_id = "file-creation-test"
        messages = [{"role": "user", "content": "Test"}]

        with patch('server.MEMORY_DIR', temp_memory_dir):
            save_conversation(session_id, messages)
            file_path = temp_memory_dir / f"{session_id}.json"

        assert file_path.exists()
        with open(file_path, 'r') as f:
            data = json.load(f)
        assert data == messages

    def test_save_conversation_unicode(self, temp_memory_dir):
        """Test saving and loading conversations with unicode characters"""
        session_id = "unicode-test"
        messages = [
            {"role": "user", "content": "Hello 你好 مرحبا"},
            {"role": "assistant", "content": "Hi! 👋 Bonjour 🇫🇷"}
        ]

        with patch('server.MEMORY_DIR', temp_memory_dir):
            save_conversation(session_id, messages)
            loaded_messages = load_conversation(session_id)

        assert loaded_messages == messages

    def test_conversation_persistence(self, temp_memory_dir):
        """Test that conversations persist across multiple saves"""
        session_id = "persistent-session"

        with patch('server.MEMORY_DIR', temp_memory_dir):
            # First save
            messages1 = [{"role": "user", "content": "First message"}]
            save_conversation(session_id, messages1)

            # Second save (append)
            messages2 = [
                {"role": "user", "content": "First message"},
                {"role": "assistant", "content": "Response"},
                {"role": "user", "content": "Second message"}
            ]
            save_conversation(session_id, messages2)

            # Load and verify
            loaded = load_conversation(session_id)

        assert len(loaded) == 3
        assert loaded[-1]["content"] == "Second message"

    def test_load_personality(self):
        """Test loading personality from me.txt"""
        # Mock the file reading
        mock_content = "I am a helpful AI assistant with expertise in coding."

        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = mock_content + "\n"
            personality = load_personality()

        assert personality == mock_content

    def test_multiple_sessions(self, temp_memory_dir):
        """Test managing multiple conversation sessions"""
        sessions = {
            "session-1": [{"role": "user", "content": "Session 1"}],
            "session-2": [{"role": "user", "content": "Session 2"}],
            "session-3": [{"role": "user", "content": "Session 3"}]
        }

        with patch('server.MEMORY_DIR', temp_memory_dir):
            # Save all sessions
            for session_id, messages in sessions.items():
                save_conversation(session_id, messages)

            # Load and verify each session
            for session_id, expected_messages in sessions.items():
                loaded = load_conversation(session_id)
                assert loaded == expected_messages

        # Verify files exist
        assert len(list(temp_memory_dir.glob("*.json"))) == 3


class TestConversationHistory:
    """Test conversation history management"""

    @pytest.fixture
    def sample_conversation(self):
        return [
            {"role": "user", "content": "What's the weather?"},
            {"role": "assistant", "content": "I don't have real-time data."},
            {"role": "user", "content": "Tell me a joke"},
            {"role": "assistant", "content": "Why did the AI cross the road?"},
        ]

    def test_conversation_length(self, sample_conversation):
        """Test tracking conversation length"""
        assert len(sample_conversation) == 4
        assert sample_conversation[0]["role"] == "user"
        assert sample_conversation[-1]["role"] == "assistant"

    def test_conversation_structure(self, sample_conversation):
        """Test that conversation alternates between user and assistant"""
        for i, msg in enumerate(sample_conversation):
            expected_role = "user" if i % 2 == 0 else "assistant"
            assert msg["role"] == expected_role
            assert "content" in msg
            assert len(msg["content"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
