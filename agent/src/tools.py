"""
Custom tools for the GPT20 agent using the @tool decorator.
"""

from strands.tools.decorator import tool
from .templates import _get_index_path, read_index_for_update as _read_index_for_update, write_index as _write_index


@tool
def read_index(index_name: str) -> dict:
    """
    Read an index file for updating.

    Args:
        index_name: Name of the index file (e.g., "GPT20")

    Returns:
        dict with 'content' and 'exists' keys
    """
    content, exists = _read_index_for_update(index_name)
    return {
        "content": content,
        "exists": exists,
        "message": f"Successfully read index file '{index_name}'" if exists else f"Index file '{index_name}' does not exist"
    }


@tool
def write_index(index_name: str, content: str) -> dict:
    """
    Write content to an index file.

    Args:
        index_name: Name of the index file (e.g., "GPT20")
        content: Content to write to the file

    Returns:
        dict with success status and file path
    """
    file_path = _write_index(index_name, content)
    return {
        "success": True,
        "file_path": str(file_path),
        "message": f"Successfully wrote {len(content)} characters to {file_path}"
    }


@tool
def get_index_info(index_name: str) -> dict:
    """
    Get information about an index file.

    Args:
        index_name: Name of the index file (e.g., "GPT20")

    Returns:
        dict with file information
    """
    index_path = _get_index_path(index_name)

    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
        return {
            "exists": True,
            "path": str(index_path),
            "size_bytes": index_path.stat().st_size,
            "content_length": len(content),
            "line_count": len(content.splitlines()),
            "message": f"Index file '{index_name}' exists with {len(content)} characters"
        }
    else:
        return {
            "exists": False,
            "path": str(index_path),
            "message": f"Index file '{index_name}' does not exist"
        }
