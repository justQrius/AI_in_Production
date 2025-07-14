"""
Usage tracking middleware for monitoring API usage per user.
Tracks idea generation counts and provides analytics data.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
import json
from pathlib import Path


class UsageTracker:
    """
    Simple in-memory usage tracker.
    In production, this would use Redis or a database.
    """

    def __init__(self):
        self._usage: Dict[str, Dict] = {}
        self._storage_path = Path(__file__).parent / "usage_data.json"
        self._load_from_disk()

    def _load_from_disk(self):
        """Load usage data from disk if available."""
        if self._storage_path.exists():
            try:
                with open(self._storage_path, 'r') as f:
                    self._usage = json.load(f)
            except Exception:
                self._usage = {}

    def _save_to_disk(self):
        """Save usage data to disk."""
        try:
            with open(self._storage_path, 'w') as f:
                json.dump(self._usage, f)
        except Exception:
            pass  # Fail silently in case of write errors

    def _get_user_data(self, user_id: str) -> Dict:
        """Get or create user usage data."""
        if user_id not in self._usage:
            self._usage[user_id] = {
                "total_ideas": 0,
                "daily_ideas": 0,
                "monthly_ideas": 0,
                "last_reset_day": datetime.now().strftime("%Y-%m-%d"),
                "last_reset_month": datetime.now().strftime("%Y-%m"),
                "history": []
            }
        return self._usage[user_id]

    def _reset_counters_if_needed(self, user_data: Dict):
        """Reset daily and monthly counters if period has passed."""
        now = datetime.now()
        current_day = now.strftime("%Y-%m-%d")
        current_month = now.strftime("%Y-%m")

        # Reset daily counter
        if user_data["last_reset_day"] != current_day:
            user_data["daily_ideas"] = 0
            user_data["last_reset_day"] = current_day

        # Reset monthly counter
        if user_data["last_reset_month"] != current_month:
            user_data["monthly_ideas"] = 0
            user_data["last_reset_month"] = current_month

    def track_idea_generation(
        self,
        user_id: str,
        template: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict:
        """
        Track an idea generation event.

        Args:
            user_id: The user's ID
            template: The template used (if any)
            language: The language used

        Returns:
            Updated usage statistics for the user
        """
        user_data = self._get_user_data(user_id)
        self._reset_counters_if_needed(user_data)

        # Increment counters
        user_data["total_ideas"] += 1
        user_data["daily_ideas"] += 1
        user_data["monthly_ideas"] += 1

        # Add to history
        event = {
            "timestamp": datetime.now().isoformat(),
            "template": template,
            "language": language
        }
        user_data["history"].append(event)

        # Keep only last 100 events to prevent unbounded growth
        if len(user_data["history"]) > 100:
            user_data["history"] = user_data["history"][-100:]

        self._save_to_disk()

        return {
            "total_ideas": user_data["total_ideas"],
            "daily_ideas": user_data["daily_ideas"],
            "monthly_ideas": user_data["monthly_ideas"],
            "ideas_remaining_today": None  # Will be calculated based on tier
        }

    def get_usage_stats(self, user_id: str) -> Dict:
        """
        Get usage statistics for a user.

        Args:
            user_id: The user's ID

        Returns:
            Dictionary containing usage statistics
        """
        user_data = self._get_user_data(user_id)
        self._reset_counters_if_needed(user_data)

        return {
            "total_ideas": user_data["total_ideas"],
            "daily_ideas": user_data["daily_ideas"],
            "monthly_ideas": user_data["monthly_ideas"],
            "last_reset_day": user_data["last_reset_day"],
            "last_reset_month": user_data["last_reset_month"],
            "recent_history": user_data["history"][-10:]  # Last 10 events
        }

    def get_analytics(self, user_id: str) -> Dict:
        """
        Get detailed analytics for a user.

        Args:
            user_id: The user's ID

        Returns:
            Dictionary containing analytics data
        """
        user_data = self._get_user_data(user_id)

        # Count template usage
        template_usage = {}
        language_usage = {}

        for event in user_data["history"]:
            template = event.get("template", "general")
            language = event.get("language", "en")

            template_usage[template] = template_usage.get(template, 0) + 1
            language_usage[language] = language_usage.get(language, 0) + 1

        return {
            "total_ideas_generated": user_data["total_ideas"],
            "this_month": user_data["monthly_ideas"],
            "today": user_data["daily_ideas"],
            "template_distribution": template_usage,
            "language_distribution": language_usage,
            "most_used_template": max(template_usage.items(), key=lambda x: x[1])[0] if template_usage else None,
            "most_used_language": max(language_usage.items(), key=lambda x: x[1])[0] if language_usage else None
        }


# Global instance
usage_tracker = UsageTracker()
