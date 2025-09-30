"""
Tests for memory persistence system.
"""

import pytest
import os
import tempfile
import shutil
from memory import FileMemoryStore


class TestFileMemoryStore:
    """Test file-based memory storage."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)

    @pytest.fixture
    def memory_store(self, temp_dir):
        """Create memory store instance."""
        return FileMemoryStore(storage_dir=temp_dir)

    def test_save_and_load_todos(self, memory_store):
        """Test saving and loading todos."""
        agent_id = "test-agent-001"
        todos = [
            {"description": "Task 1", "completed": False},
            {"description": "Task 2", "completed": True}
        ]

        # Save todos
        assert memory_store.save_todos(agent_id, todos)

        # Load todos
        loaded_todos = memory_store.load_todos(agent_id)
        assert loaded_todos == todos

    def test_load_nonexistent_todos(self, memory_store):
        """Test loading todos for non-existent agent."""
        todos = memory_store.load_todos("nonexistent-agent")
        assert todos == []

    def test_save_and_load_state(self, memory_store):
        """Test saving and loading agent state."""
        agent_id = "test-agent-002"
        state = {
            "current_step": 5,
            "context": {"key": "value"},
            "variables": [1, 2, 3]
        }

        # Save state
        assert memory_store.save_agent_state(agent_id, state)

        # Load state
        loaded_state = memory_store.load_agent_state(agent_id)
        assert loaded_state == state

    def test_list_sessions(self, memory_store):
        """Test listing agent sessions."""
        # Create multiple sessions
        memory_store.save_todos("agent-1", [{"description": "Task"}])
        memory_store.save_todos("agent-2", [{"description": "Task"}])
        memory_store.save_todos("agent-3", [{"description": "Task"}])

        # List sessions
        sessions = memory_store.list_agent_sessions()
        assert len(sessions) == 3
        assert "agent-1" in sessions
        assert "agent-2" in sessions
        assert "agent-3" in sessions

    def test_delete_session(self, memory_store):
        """Test deleting agent session."""
        agent_id = "test-agent-delete"
        todos = [{"description": "Task"}]

        # Create session
        memory_store.save_todos(agent_id, todos)
        assert len(memory_store.load_todos(agent_id)) > 0

        # Delete session
        assert memory_store.delete_session(agent_id)

        # Verify deletion
        assert memory_store.load_todos(agent_id) == []
