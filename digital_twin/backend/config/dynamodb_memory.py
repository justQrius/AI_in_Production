"""
DynamoDB-based memory storage for production deployments.
Provides scalable, persistent conversation history storage.
"""

import boto3
from boto3.dynamodb.conditions import Key
from typing import List, Dict, Optional
from datetime import datetime
import json
import os


class DynamoDBMemoryStore:
    """DynamoDB implementation of conversation memory storage"""

    def __init__(self, table_name: str = "DigitalTwinConversations"):
        """
        Initialize DynamoDB client and table reference.

        Args:
            table_name: Name of the DynamoDB table
        """
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = table_name
        self.table = self.dynamodb.Table(table_name)

    def save_conversation(
        self,
        session_id: str,
        messages: List[Dict],
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Save conversation to DynamoDB.

        Args:
            session_id: Unique session identifier
            messages: List of conversation messages
            metadata: Optional metadata about the conversation
        """
        item = {
            'session_id': session_id,
            'messages': messages,
            'message_count': len(messages),
            'last_updated': datetime.utcnow().isoformat(),
            'created_at': metadata.get('created_at', datetime.utcnow().isoformat())
            if metadata else datetime.utcnow().isoformat()
        }

        if metadata:
            item['metadata'] = metadata

        self.table.put_item(Item=item)

    def load_conversation(self, session_id: str) -> List[Dict]:
        """
        Load conversation from DynamoDB.

        Args:
            session_id: Unique session identifier

        Returns:
            List of conversation messages
        """
        try:
            response = self.table.get_item(Key={'session_id': session_id})
            if 'Item' in response:
                return response['Item'].get('messages', [])
            return []
        except Exception as e:
            print(f"Error loading conversation: {e}")
            return []

    def list_sessions(
        self,
        limit: int = 100,
        last_key: Optional[str] = None
    ) -> Dict:
        """
        List all conversation sessions.

        Args:
            limit: Maximum number of sessions to return
            last_key: Pagination key for next page

        Returns:
            Dictionary with sessions and pagination info
        """
        scan_kwargs = {'Limit': limit}

        if last_key:
            scan_kwargs['ExclusiveStartKey'] = {'session_id': last_key}

        response = self.table.scan(**scan_kwargs)

        sessions = []
        for item in response.get('Items', []):
            sessions.append({
                'session_id': item['session_id'],
                'message_count': item.get('message_count', 0),
                'last_updated': item.get('last_updated'),
                'created_at': item.get('created_at'),
                'last_message': item['messages'][-1]['content']
                if item.get('messages') else None
            })

        return {
            'sessions': sessions,
            'last_key': response.get('LastEvaluatedKey', {}).get('session_id'),
            'count': len(sessions)
        }

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a conversation session.

        Args:
            session_id: Unique session identifier

        Returns:
            True if deleted, False otherwise
        """
        try:
            self.table.delete_item(Key={'session_id': session_id})
            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False

    def get_session_stats(self, session_id: str) -> Optional[Dict]:
        """
        Get statistics for a specific session.

        Args:
            session_id: Unique session identifier

        Returns:
            Dictionary with session statistics
        """
        try:
            response = self.table.get_item(Key={'session_id': session_id})
            if 'Item' in response:
                item = response['Item']
                messages = item.get('messages', [])

                return {
                    'session_id': session_id,
                    'total_messages': len(messages),
                    'user_messages': sum(1 for m in messages if m['role'] == 'user'),
                    'assistant_messages': sum(1 for m in messages if m['role'] == 'assistant'),
                    'created_at': item.get('created_at'),
                    'last_updated': item.get('last_updated'),
                    'duration_minutes': self._calculate_duration(item)
                }
            return None
        except Exception as e:
            print(f"Error getting session stats: {e}")
            return None

    def _calculate_duration(self, item: Dict) -> Optional[float]:
        """Calculate conversation duration in minutes"""
        try:
            created = datetime.fromisoformat(item['created_at'])
            updated = datetime.fromisoformat(item['last_updated'])
            return (updated - created).total_seconds() / 60
        except:
            return None


# Terraform configuration for DynamoDB table creation
TERRAFORM_CONFIG = """
resource "aws_dynamodb_table" "digital_twin_conversations" {
  name           = "DigitalTwinConversations"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "session_id"

  attribute {
    name = "session_id"
    type = "S"
  }

  attribute {
    name = "last_updated"
    type = "S"
  }

  global_secondary_index {
    name            = "LastUpdatedIndex"
    hash_key        = "session_id"
    range_key       = "last_updated"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Name        = "DigitalTwinConversations"
    Environment = "production"
    Project     = "DigitalTwin"
  }
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.digital_twin_conversations.name
}

output "dynamodb_table_arn" {
  value = aws_dynamodb_table.digital_twin_conversations.arn
}
"""


def create_table_if_not_exists(table_name: str = "DigitalTwinConversations"):
    """
    Create DynamoDB table if it doesn't exist.
    For use in development/testing environments.
    """
    dynamodb = boto3.resource('dynamodb')

    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'session_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'session_id', 'AttributeType': 'S'},
                {'AttributeName': 'last_updated', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'LastUpdatedIndex',
                    'KeySchema': [
                        {'AttributeName': 'session_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'last_updated', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        # Wait for table to be created
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f"Table {table_name} created successfully")
        return True

    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print(f"Table {table_name} already exists")
        return True
    except Exception as e:
        print(f"Error creating table: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    store = DynamoDBMemoryStore()

    # Test save
    test_messages = [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there!"}
    ]
    store.save_conversation("test-session", test_messages)

    # Test load
    loaded = store.load_conversation("test-session")
    print(f"Loaded {len(loaded)} messages")

    # Test list
    sessions = store.list_sessions()
    print(f"Found {sessions['count']} sessions")
