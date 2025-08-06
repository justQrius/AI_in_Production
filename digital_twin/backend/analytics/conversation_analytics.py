"""
Conversation analytics for Digital Twin.
Tracks usage patterns, popular topics, and conversation quality metrics.
"""

from typing import List, Dict, Optional
from collections import Counter
from datetime import datetime, timedelta
import re
import json
from pathlib import Path


class ConversationAnalytics:
    """Analytics engine for conversation data"""

    def __init__(self, memory_dir: Path = None):
        """
        Initialize analytics engine.

        Args:
            memory_dir: Path to conversation storage directory
        """
        self.memory_dir = memory_dir or Path("../memory")

    def analyze_conversation(self, messages: List[Dict]) -> Dict:
        """
        Analyze a single conversation.

        Args:
            messages: List of conversation messages

        Returns:
            Dictionary with conversation metrics
        """
        if not messages:
            return self._empty_metrics()

        user_messages = [m for m in messages if m["role"] == "user"]
        assistant_messages = [m for m in messages if m["role"] == "assistant"]

        return {
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "avg_user_message_length": self._avg_length(user_messages),
            "avg_assistant_message_length": self._avg_length(assistant_messages),
            "conversation_turns": len(user_messages),
            "total_words": self._count_words(messages),
            "question_count": self._count_questions(user_messages),
            "topics": self._extract_topics(messages),
            "sentiment": self._analyze_sentiment(messages)
        }

    def get_global_analytics(self) -> Dict:
        """
        Get analytics across all conversations.

        Returns:
            Dictionary with global metrics
        """
        all_conversations = []
        session_count = 0

        for file_path in self.memory_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    conversation = json.load(f)
                    all_conversations.append(conversation)
                    session_count += 1
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

        if not all_conversations:
            return self._empty_global_metrics()

        # Aggregate metrics
        total_messages = sum(len(c) for c in all_conversations)
        total_user_messages = sum(
            len([m for m in c if m["role"] == "user"])
            for c in all_conversations
        )

        all_messages = [msg for conv in all_conversations for msg in conv]

        return {
            "total_sessions": session_count,
            "total_messages": total_messages,
            "total_user_messages": total_user_messages,
            "avg_messages_per_session": total_messages / session_count if session_count > 0 else 0,
            "most_active_day": self._find_most_active_period(all_conversations),
            "common_topics": self._extract_common_topics(all_messages, top_n=10),
            "avg_conversation_length": self._avg_conversation_length(all_conversations),
            "question_rate": self._calculate_question_rate(all_messages)
        }

    def get_time_series_metrics(
        self,
        days: int = 30,
        granularity: str = "day"
    ) -> List[Dict]:
        """
        Get time-series metrics for visualization.

        Args:
            days: Number of days to analyze
            granularity: Time granularity ("hour", "day", "week")

        Returns:
            List of metrics by time period
        """
        metrics = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # This is a simplified implementation
        # In production, this would query DynamoDB with time-based indexes
        return metrics

    def _avg_length(self, messages: List[Dict]) -> float:
        """Calculate average message length in characters"""
        if not messages:
            return 0.0
        lengths = [len(m.get("content", "")) for m in messages]
        return sum(lengths) / len(lengths)

    def _count_words(self, messages: List[Dict]) -> int:
        """Count total words across all messages"""
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            total += len(content.split())
        return total

    def _count_questions(self, messages: List[Dict]) -> int:
        """Count number of questions in user messages"""
        count = 0
        for msg in messages:
            content = msg.get("content", "")
            # Simple heuristic: count sentences ending with ?
            count += content.count("?")
        return count

    def _extract_topics(self, messages: List[Dict]) -> List[str]:
        """
        Extract main topics from conversation.
        Simplified implementation using keyword extraction.
        """
        all_text = " ".join(m.get("content", "") for m in messages)
        words = re.findall(r'\b\w{4,}\b', all_text.lower())

        # Filter common words (simplified stop words)
        stop_words = {"that", "this", "with", "have", "from", "they", "what",
                     "about", "which", "their", "there", "would", "could"}
        words = [w for w in words if w not in stop_words]

        # Get most common words as topics
        counter = Counter(words)
        return [word for word, count in counter.most_common(5)]

    def _analyze_sentiment(self, messages: List[Dict]) -> str:
        """
        Basic sentiment analysis.
        Returns: "positive", "neutral", or "negative"
        """
        # Simplified sentiment analysis using keyword matching
        positive_words = {"great", "good", "thanks", "awesome", "excellent", "love"}
        negative_words = {"bad", "wrong", "error", "problem", "issue", "hate"}

        all_text = " ".join(m.get("content", "").lower() for m in messages)
        words = set(re.findall(r'\b\w+\b', all_text))

        positive_score = len(words & positive_words)
        negative_score = len(words & negative_words)

        if positive_score > negative_score:
            return "positive"
        elif negative_score > positive_score:
            return "negative"
        return "neutral"

    def _extract_common_topics(self, messages: List[Dict], top_n: int = 10) -> List[Dict]:
        """Extract most common topics across all conversations"""
        all_words = []
        for msg in messages:
            content = msg.get("content", "").lower()
            words = re.findall(r'\b\w{4,}\b', content)
            all_words.extend(words)

        counter = Counter(all_words)
        return [
            {"topic": word, "count": count}
            for word, count in counter.most_common(top_n)
        ]

    def _avg_conversation_length(self, conversations: List[List[Dict]]) -> float:
        """Calculate average conversation length in messages"""
        if not conversations:
            return 0.0
        lengths = [len(c) for c in conversations]
        return sum(lengths) / len(lengths)

    def _calculate_question_rate(self, messages: List[Dict]) -> float:
        """Calculate percentage of messages that are questions"""
        if not messages:
            return 0.0
        questions = sum(1 for m in messages if "?" in m.get("content", ""))
        return (questions / len(messages)) * 100

    def _find_most_active_period(self, conversations: List[List[Dict]]) -> str:
        """
        Find the most active time period.
        In production, this would use actual timestamps.
        """
        return "weekdays"  # Placeholder

    def _empty_metrics(self) -> Dict:
        """Return empty metrics structure"""
        return {
            "total_messages": 0,
            "user_messages": 0,
            "assistant_messages": 0,
            "avg_user_message_length": 0.0,
            "avg_assistant_message_length": 0.0,
            "conversation_turns": 0,
            "total_words": 0,
            "question_count": 0,
            "topics": [],
            "sentiment": "neutral"
        }

    def _empty_global_metrics(self) -> Dict:
        """Return empty global metrics structure"""
        return {
            "total_sessions": 0,
            "total_messages": 0,
            "total_user_messages": 0,
            "avg_messages_per_session": 0.0,
            "most_active_day": "N/A",
            "common_topics": [],
            "avg_conversation_length": 0.0,
            "question_rate": 0.0
        }


# Example usage
if __name__ == "__main__":
    analytics = ConversationAnalytics()

    # Example conversation
    sample_conversation = [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing great! How can I help you today?"},
        {"role": "user", "content": "I have a question about AI technology."},
        {"role": "assistant", "content": "I'd be happy to discuss AI technology with you. What would you like to know?"}
    ]

    # Analyze single conversation
    metrics = analytics.analyze_conversation(sample_conversation)
    print(json.dumps(metrics, indent=2))

    # Get global analytics (if memory directory exists)
    if analytics.memory_dir.exists():
        global_metrics = analytics.get_global_analytics()
        print("\nGlobal Analytics:")
        print(json.dumps(global_metrics, indent=2))
