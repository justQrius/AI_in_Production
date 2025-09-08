#!/usr/bin/env python3
"""Package Rebalancer Lambda using Docker"""

import subprocess
from pathlib import Path

def package_lambda():
    agent_dir = Path(__file__).parent
    backend_dir = agent_dir.parent
    output_file = agent_dir / "rebalancer_lambda.zip"

    if output_file.exists():
        output_file.unlink()

    print(f"Packaging Rebalancer agent...")

    subprocess.run([
        "docker", "run", "--rm",
        "-v", f"{agent_dir}:/workspace",
        "-v", f"{backend_dir}/database:/workspace/database",
        "-w", "/workspace",
        "--platform", "linux/amd64",
        "python:3.11-slim",
        "bash", "-c",
        """
        pip install --target ./package -r <(cat <<EOF
openai-agents
litellm
tenacity
boto3
pydantic
psycopg2-binary
langfuse
logfire
EOF
        ) && \
        cd package && zip -r ../rebalancer_lambda.zip . && cd .. && \
        zip rebalancer_lambda.zip lambda_handler.py agent.py templates.py observability.py && \
        cd database/src && zip ../../rebalancer_lambda.zip *.py
        """
    ], check=True)

    size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"✅ Created {output_file.name} ({size_mb:.1f} MB)")

if __name__ == "__main__":
    package_lambda()
