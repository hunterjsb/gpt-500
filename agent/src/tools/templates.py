"""Template and index file utilities."""

from pathlib import Path
from string import Template
from strands.tools.decorator import tool


class TemplateLoader:
    def __init__(self, templates_dir=None):
        self.templates_dir = templates_dir or Path(__file__).parent.parent.parent / "md" / "prompts"

    def load_template(self, template_name):
        if not template_name.endswith(".md"):
            template_name += ".md"
        template_path = self.templates_dir / template_name
        return template_path.read_text(encoding="utf-8")

    def format_template(self, template_name, **kwargs):
        template_content = self.load_template(template_name)
        template = Template(template_content)
        return template.safe_substitute(**kwargs)


# Default loader instance
_loader = TemplateLoader()
load_template = _loader.load_template
format_template = _loader.format_template


def _get_index_path(index_name):
    if not index_name.endswith(".md"):
        index_name += ".md"
    return Path(__file__).parent.parent.parent / "md" / "indices" / index_name


def _read_index_for_update(index_name):
    index_path = _get_index_path(index_name)
    if index_path.exists():
        return index_path.read_text(encoding="utf-8"), True
    return "FILE IS EMPTY - CREATE THE INITIAL INDEX", False


def _write_index(index_name, content):
    index_path = _get_index_path(index_name)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(content, encoding="utf-8")
    return index_path


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
        "message": (
            f"Successfully read index file '{index_name}'" if exists else f"Index file '{index_name}' does not exist"
        ),
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
        "message": f"Successfully wrote {len(content)} characters to {file_path}",
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
            "message": f"Index file '{index_name}' exists with {len(content)} characters",
        }
    else:
        return {"exists": False, "path": str(index_path), "message": f"Index file '{index_name}' does not exist"}
