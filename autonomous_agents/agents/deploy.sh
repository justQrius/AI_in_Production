#!/bin/bash

# Configure the agent (interactive)
uv run agentcore configure -e looper.py

# Launch the agent
uv run agentcore launch

# Invoke the agent with a test prompt
uv run agentcore invoke '{"prompt": "A train leaves Boston at 2:00 pm traveling 60 mph. Another train leaves New York at 3:00 pm traveling 80 mph toward Boston. When do they meet?"}'
