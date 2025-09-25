"""
File operation tools for autonomous agents.
Provides safe file read/write capabilities with sandboxing.
"""

import os
import json
from pathlib import Path
from typing import Optional
from strands import tool


# Sandbox directory for agent file operations
SANDBOX_DIR = Path(os.getenv("AGENT_SANDBOX_DIR", "./agent_workspace"))
SANDBOX_DIR.mkdir(exist_ok=True)


def _get_safe_path(filename: str) -> Optional[Path]:
    """Get safe path within sandbox directory."""
    try:
        # Resolve to absolute path and ensure it's within sandbox
        file_path = (SANDBOX_DIR / filename).resolve()

        # Security check: ensure path is within sandbox
        if not str(file_path).startswith(str(SANDBOX_DIR.resolve())):
            return None

        return file_path
    except Exception:
        return None


@tool
def read_file(filename: str) -> str:
    """
    Read contents of a file from the agent workspace.

    Args:
        filename: Name of file to read (relative to workspace)

    Returns:
        File contents as string, or error message
    """
    file_path = _get_safe_path(filename)

    if not file_path:
        return json.dumps({"error": "Invalid file path"})

    if not file_path.exists():
        return json.dumps({"error": f"File not found: {filename}"})

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return json.dumps({
            "filename": filename,
            "content": content,
            "size_bytes": len(content)
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to read file: {str(e)}"})


@tool
def write_file(filename: str, content: str) -> str:
    """
    Write content to a file in the agent workspace.

    Args:
        filename: Name of file to write
        content: Content to write to file

    Returns:
        Success message or error
    """
    file_path = _get_safe_path(filename)

    if not file_path:
        return json.dumps({"error": "Invalid file path"})

    try:
        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return json.dumps({
            "success": True,
            "filename": filename,
            "bytes_written": len(content)
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to write file: {str(e)}"})


@tool
def list_files(directory: str = ".") -> str:
    """
    List files in a directory within the agent workspace.

    Args:
        directory: Directory to list (relative to workspace, default: ".")

    Returns:
        JSON list of files and directories
    """
    dir_path = _get_safe_path(directory)

    if not dir_path:
        return json.dumps({"error": "Invalid directory path"})

    if not dir_path.exists():
        return json.dumps({"error": f"Directory not found: {directory}"})

    try:
        items = []
        for item in dir_path.iterdir():
            items.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size_bytes": item.stat().st_size if item.is_file() else 0
            })

        # Sort: directories first, then files
        items.sort(key=lambda x: (x["type"] == "file", x["name"]))

        return json.dumps({
            "directory": directory,
            "item_count": len(items),
            "items": items
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to list directory: {str(e)}"})


@tool
def delete_file(filename: str) -> str:
    """
    Delete a file from the agent workspace.

    Args:
        filename: Name of file to delete

    Returns:
        Success message or error
    """
    file_path = _get_safe_path(filename)

    if not file_path:
        return json.dumps({"error": "Invalid file path"})

    if not file_path.exists():
        return json.dumps({"error": f"File not found: {filename}"})

    try:
        file_path.unlink()
        return json.dumps({
            "success": True,
            "message": f"Deleted file: {filename}"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to delete file: {str(e)}"})
