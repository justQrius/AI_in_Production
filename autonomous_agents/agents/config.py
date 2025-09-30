"""
Configuration management for autonomous agents.
Centralized configuration with environment variable support.
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class AgentConfig:
    """Agent configuration settings."""

    # AWS Settings
    aws_region: str = "us-west-2"
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"

    # Memory Settings
    use_dynamodb: bool = False
    memory_table_name: str = "autonomous-agent-memory"
    file_memory_dir: str = "./memory"

    # Tool Settings
    enable_web_search: bool = True
    enable_file_operations: bool = True
    enable_code_interpreter: bool = True
    sandbox_dir: str = "./agent_workspace"

    # Performance Settings
    max_iterations: int = 20
    timeout_seconds: int = 300
    max_tokens: int = 4096

    # Analytics Settings
    enable_analytics: bool = True
    log_level: str = "INFO"

    # Safety Settings
    allow_internet_access: bool = True
    allow_file_write: bool = True
    max_file_size_mb: int = 10

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Create configuration from environment variables."""
        return cls(
            aws_region=os.getenv("AWS_REGION", "us-west-2"),
            bedrock_model_id=os.getenv(
                "BEDROCK_MODEL_ID",
                "anthropic.claude-3-sonnet-20240229-v1:0"
            ),
            use_dynamodb=os.getenv("USE_DYNAMODB", "false").lower() == "true",
            memory_table_name=os.getenv("AGENT_MEMORY_TABLE", "autonomous-agent-memory"),
            file_memory_dir=os.getenv("FILE_MEMORY_DIR", "./memory"),
            enable_web_search=os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true",
            enable_file_operations=os.getenv("ENABLE_FILE_OPS", "true").lower() == "true",
            enable_code_interpreter=os.getenv("ENABLE_CODE_INTERPRETER", "true").lower() == "true",
            sandbox_dir=os.getenv("AGENT_SANDBOX_DIR", "./agent_workspace"),
            max_iterations=int(os.getenv("MAX_ITERATIONS", "20")),
            timeout_seconds=int(os.getenv("TIMEOUT_SECONDS", "300")),
            max_tokens=int(os.getenv("MAX_TOKENS", "4096")),
            enable_analytics=os.getenv("ENABLE_ANALYTICS", "true").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            allow_internet_access=os.getenv("ALLOW_INTERNET", "true").lower() == "true",
            allow_file_write=os.getenv("ALLOW_FILE_WRITE", "true").lower() == "true",
            max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", "10"))
        )

    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "aws_region": self.aws_region,
            "bedrock_model_id": self.bedrock_model_id,
            "use_dynamodb": self.use_dynamodb,
            "memory_table_name": self.memory_table_name,
            "enable_web_search": self.enable_web_search,
            "enable_file_operations": self.enable_file_operations,
            "enable_code_interpreter": self.enable_code_interpreter,
            "max_iterations": self.max_iterations,
            "timeout_seconds": self.timeout_seconds,
            "enable_analytics": self.enable_analytics
        }


# Global configuration instance
_config: Optional[AgentConfig] = None


def get_config() -> AgentConfig:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = AgentConfig.from_env()
    return _config


def reload_config():
    """Reload configuration from environment."""
    global _config
    _config = AgentConfig.from_env()
