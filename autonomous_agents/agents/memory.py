"""
Memory persistence system for autonomous agents.
Stores todo lists and agent state in DynamoDB.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError


class MemoryStore:
    """Persistent memory storage for agent state."""

    def __init__(self, table_name: str = None):
        """Initialize memory store with DynamoDB table."""
        self.table_name = table_name or os.getenv("AGENT_MEMORY_TABLE", "autonomous-agent-memory")
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(self.table_name)

    def save_todos(self, agent_id: str, todos: List[Dict[str, Any]]) -> bool:
        """Save todos list for an agent."""
        try:
            item = {
                'agent_id': agent_id,
                'todos': todos,
                'last_updated': datetime.utcnow().isoformat(),
                'todo_count': len(todos)
            }
            self.table.put_item(Item=item)
            return True
        except ClientError as e:
            print(f"Error saving todos: {e}")
            return False

    def load_todos(self, agent_id: str) -> List[Dict[str, Any]]:
        """Load todos list for an agent."""
        try:
            response = self.table.get_item(Key={'agent_id': agent_id})
            if 'Item' in response:
                return response['Item'].get('todos', [])
            return []
        except ClientError as e:
            print(f"Error loading todos: {e}")
            return []

    def save_agent_state(self, agent_id: str, state: Dict[str, Any]) -> bool:
        """Save complete agent state."""
        try:
            item = {
                'agent_id': f"{agent_id}#state",
                'state': state,
                'last_updated': datetime.utcnow().isoformat()
            }
            self.table.put_item(Item=item)
            return True
        except ClientError as e:
            print(f"Error saving state: {e}")
            return False

    def load_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load complete agent state."""
        try:
            response = self.table.get_item(Key={'agent_id': f"{agent_id}#state"})
            if 'Item' in response:
                return response['Item'].get('state')
            return None
        except ClientError as e:
            print(f"Error loading state: {e}")
            return None

    def list_agent_sessions(self, limit: int = 50) -> List[str]:
        """List all agent session IDs."""
        try:
            response = self.table.scan(Limit=limit)
            sessions = []
            for item in response.get('Items', []):
                agent_id = item.get('agent_id', '')
                if not agent_id.endswith('#state'):
                    sessions.append(agent_id)
            return sessions
        except ClientError as e:
            print(f"Error listing sessions: {e}")
            return []

    def delete_session(self, agent_id: str) -> bool:
        """Delete agent session and state."""
        try:
            self.table.delete_item(Key={'agent_id': agent_id})
            self.table.delete_item(Key={'agent_id': f"{agent_id}#state"})
            return True
        except ClientError as e:
            print(f"Error deleting session: {e}")
            return False


# Fallback to file-based storage if DynamoDB not available
class FileMemoryStore:
    """File-based memory storage for local development."""

    def __init__(self, storage_dir: str = "./memory"):
        """Initialize file-based storage."""
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def save_todos(self, agent_id: str, todos: List[Dict[str, Any]]) -> bool:
        """Save todos to JSON file."""
        try:
            file_path = os.path.join(self.storage_dir, f"{agent_id}.json")
            data = {
                'todos': todos,
                'last_updated': datetime.utcnow().isoformat(),
                'todo_count': len(todos)
            }
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving todos: {e}")
            return False

    def load_todos(self, agent_id: str) -> List[Dict[str, Any]]:
        """Load todos from JSON file."""
        try:
            file_path = os.path.join(self.storage_dir, f"{agent_id}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return data.get('todos', [])
            return []
        except Exception as e:
            print(f"Error loading todos: {e}")
            return []

    def save_agent_state(self, agent_id: str, state: Dict[str, Any]) -> bool:
        """Save agent state to JSON file."""
        try:
            file_path = os.path.join(self.storage_dir, f"{agent_id}_state.json")
            data = {
                'state': state,
                'last_updated': datetime.utcnow().isoformat()
            }
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving state: {e}")
            return False

    def load_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load agent state from JSON file."""
        try:
            file_path = os.path.join(self.storage_dir, f"{agent_id}_state.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return data.get('state')
            return None
        except Exception as e:
            print(f"Error loading state: {e}")
            return None

    def list_agent_sessions(self, limit: int = 50) -> List[str]:
        """List all agent session IDs."""
        try:
            sessions = []
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json') and not filename.endswith('_state.json'):
                    sessions.append(filename.replace('.json', ''))
            return sessions[:limit]
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []

    def delete_session(self, agent_id: str) -> bool:
        """Delete agent session files."""
        try:
            os.remove(os.path.join(self.storage_dir, f"{agent_id}.json"))
            state_file = os.path.join(self.storage_dir, f"{agent_id}_state.json")
            if os.path.exists(state_file):
                os.remove(state_file)
            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False


def get_memory_store() -> MemoryStore:
    """Get appropriate memory store based on environment."""
    use_dynamodb = os.getenv("USE_DYNAMODB", "false").lower() == "true"

    if use_dynamodb:
        return MemoryStore()
    else:
        return FileMemoryStore()
