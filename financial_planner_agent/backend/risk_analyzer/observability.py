"""Observability module for LangFuse integration."""

import os
import logging
from contextlib import contextmanager

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@contextmanager
def observe():
    """Context manager for observability with LangFuse."""
    has_langfuse = bool(os.getenv("LANGFUSE_SECRET_KEY"))

    if not has_langfuse:
        yield None
        return

    langfuse_client = None

    try:
        import logfire
        from langfuse import get_client

        logfire.configure(service_name="alex_risk_analyzer_agent", send_to_logfire=False)
        logfire.instrument_openai_agents()
        langfuse_client = get_client()
        logger.info("🎯 Observability: Setup complete")

    except (ImportError, Exception) as e:
        logger.error(f"❌ Observability: Setup failed: {e}")
        langfuse_client = None

    try:
        yield langfuse_client
    finally:
        if langfuse_client:
            try:
                langfuse_client.flush()
                langfuse_client.shutdown()
                import time
                time.sleep(10)
                logger.info("✅ Observability: Traces flushed")
            except Exception as e:
                logger.error(f"❌ Observability: Failed to flush: {e}")
