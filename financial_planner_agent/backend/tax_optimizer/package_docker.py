#!/usr/bin/env python3
"""
Package Tax Optimizer Lambda using Docker for linux/amd64 compatibility
"""

import subprocess
import os
import shutil
from pathlib import Path

def package_lambda():
    """Package Lambda function with dependencies using Docker"""

    agent_dir = Path(__file__).parent
    backend_dir = agent_dir.parent
    output_file = agent_dir / "tax_optimizer_lambda.zip"

    # Remove existing package
    if output_file.exists():
        output_file.unlink()
        print(f"Removed existing {output_file.name}")

    print(f"Packaging Tax Optimizer agent from {agent_dir}")
    print("Using Docker for linux/amd64 compatibility...")

    # Build the package using Docker
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
        cd package && \
        zip -r ../tax_optimizer_lambda.zip . && \
        cd .. && \
        zip tax_optimizer_lambda.zip lambda_handler.py agent.py templates.py observability.py && \
        cd database/src && \
        zip ../../tax_optimizer_lambda.zip *.py
        """
    ], check=True)

    # Check file size
    size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"✅ Created {output_file.name} ({size_mb:.1f} MB)")

    if size_mb > 50:
        print(f"⚠️  Package is large ({size_mb:.1f} MB) - will be uploaded to S3 by Terraform")

if __name__ == "__main__":
    package_lambda()
