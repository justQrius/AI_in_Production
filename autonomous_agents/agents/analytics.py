"""
Analytics and monitoring for autonomous agents.
Tracks agent performance, tool usage, and execution metrics.
"""

import json
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict


class AgentAnalytics:
    """Track and analyze agent performance metrics."""

    def __init__(self):
        """Initialize analytics tracker."""
        self.metrics = {
            "tool_usage": defaultdict(int),
            "execution_times": [],
            "errors": [],
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_tokens": 0
        }
        self.session_start = datetime.utcnow()

    def track_tool_use(self, tool_name: str):
        """Track usage of a specific tool."""
        self.metrics["tool_usage"][tool_name] += 1

    def track_execution_time(self, duration_ms: float):
        """Track execution time for an operation."""
        self.metrics["execution_times"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "duration_ms": duration_ms
        })

    def track_error(self, error: str, context: Dict[str, Any] = None):
        """Track an error occurrence."""
        self.metrics["errors"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "error": error,
            "context": context or {}
        })

    def track_task_completion(self, success: bool = True):
        """Track task completion or failure."""
        if success:
            self.metrics["tasks_completed"] += 1
        else:
            self.metrics["tasks_failed"] += 1

    def track_tokens(self, token_count: int):
        """Track token usage."""
        self.metrics["total_tokens"] += token_count

    def get_summary(self) -> Dict[str, Any]:
        """Get analytics summary."""
        session_duration = (datetime.utcnow() - self.session_start).total_seconds()

        # Calculate average execution time
        avg_exec_time = 0
        if self.metrics["execution_times"]:
            avg_exec_time = sum(
                e["duration_ms"] for e in self.metrics["execution_times"]
            ) / len(self.metrics["execution_times"])

        # Most used tools
        sorted_tools = sorted(
            self.metrics["tool_usage"].items(),
            key=lambda x: x[1],
            reverse=True
        )

        return {
            "session_duration_seconds": round(session_duration, 2),
            "tasks_completed": self.metrics["tasks_completed"],
            "tasks_failed": self.metrics["tasks_failed"],
            "success_rate": self._calculate_success_rate(),
            "total_tool_calls": sum(self.metrics["tool_usage"].values()),
            "most_used_tools": sorted_tools[:5],
            "avg_execution_time_ms": round(avg_exec_time, 2),
            "total_errors": len(self.metrics["errors"]),
            "total_tokens_used": self.metrics["total_tokens"],
            "calls_per_minute": round(
                sum(self.metrics["tool_usage"].values()) / (session_duration / 60), 2
            ) if session_duration > 0 else 0
        }

    def _calculate_success_rate(self) -> float:
        """Calculate task success rate percentage."""
        total = self.metrics["tasks_completed"] + self.metrics["tasks_failed"]
        if total == 0:
            return 0.0
        return round((self.metrics["tasks_completed"] / total) * 100, 2)

    def get_error_report(self) -> List[Dict[str, Any]]:
        """Get detailed error report."""
        return self.metrics["errors"]

    def export_metrics(self) -> str:
        """Export metrics as JSON."""
        return json.dumps({
            "session_start": self.session_start.isoformat(),
            "summary": self.get_summary(),
            "detailed_metrics": {
                "tool_usage": dict(self.metrics["tool_usage"]),
                "execution_times": self.metrics["execution_times"][-100:],  # Last 100
                "recent_errors": self.metrics["errors"][-20:]  # Last 20
            }
        }, indent=2)

    def reset(self):
        """Reset all metrics."""
        self.__init__()


# Global analytics instance
_analytics = AgentAnalytics()


def get_analytics() -> AgentAnalytics:
    """Get global analytics instance."""
    return _analytics
