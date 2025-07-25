"""
Template loading utilities for markdown prompt templates.
"""

from pathlib import Path
from typing import Any, Optional


class TemplateLoader:
    """Utility class for loading and formatting markdown templates."""

    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize the template loader.

        Args:
            templates_dir: Directory containing template files.
                          Defaults to ../md/prompts/ relative to this file.
        """
        if templates_dir is None:
            self.templates_dir = Path(__file__).parent.parent / "md" / "prompts"
        else:
            self.templates_dir = templates_dir

    def load_template(self, template_name: str) -> str:
        """
        Load a template file by name.

        Args:
            template_name: Name of the template file (with or without .md extension)

        Returns:
            Raw template content as string

        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        # Add .md extension if not present
        if not template_name.endswith(".md"):
            template_name += ".md"

        template_path = self.templates_dir / template_name

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        return template_path.read_text(encoding="utf-8")

    def format_template(self, template_name: str, **kwargs: Any) -> str:
        """
        Load and format a template with the provided variables.

        Args:
            template_name: Name of the template file
            **kwargs: Variables to substitute in the template

        Returns:
            Formatted template string

        Raises:
            FileNotFoundError: If template file doesn't exist
            KeyError: If template references undefined variables
        """
        template_content = self.load_template(template_name)
        return template_content.format(**kwargs)

    def safe_format_template(self, template_name: str, **kwargs: Any) -> str:
        """
        Load and format a template, ignoring missing variables.

        Args:
            template_name: Name of the template file
            **kwargs: Variables to substitute in the template

        Returns:
            Formatted template string with missing variables left as-is

        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        template_content = self.load_template(template_name)

        # Use string.Template for safe substitution
        from string import Template

        template = Template(template_content)
        return template.safe_substitute(**kwargs)

    def list_templates(self) -> list[str]:
        """
        List all available template files.

        Returns:
            List of template filenames (without .md extension)
        """
        if not self.templates_dir.exists():
            return []

        templates = []
        for template_file in self.templates_dir.glob("*.md"):
            templates.append(template_file.stem)

        return sorted(templates)


# Convenience functions using default template loader
_default_loader = TemplateLoader()


def load_template(template_name: str) -> str:
    """Load a template using the default template loader."""
    return _default_loader.load_template(template_name)


def format_template(template_name: str, **kwargs: Any) -> str:
    """Format a template using the default template loader."""
    return _default_loader.format_template(template_name, **kwargs)


def safe_format_template(template_name: str, **kwargs: Any) -> str:
    """Safely format a template using the default template loader."""
    return _default_loader.safe_format_template(template_name, **kwargs)


def list_templates() -> list[str]:
    """List available templates using the default template loader."""
    return _default_loader.list_templates()


def _get_index_path(index_name: str) -> Path:
    """Get the full path for an index file."""
    if not index_name.endswith(".md"):
        index_name += ".md"
    return Path(__file__).parent.parent / "md" / "indices" / index_name


def read_index_for_update(index_name: str) -> tuple[str, bool]:
    """Read an index file, returning content or empty message."""
    index_path = _get_index_path(index_name)
    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
        return content, True
    else:
        return "FILE IS EMPTY - CREATE THE INITIAL INDEX", False


def write_index(index_name: str, content: str) -> Path:
    """Write content to an index file."""
    index_path = _get_index_path(index_name)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(content, encoding="utf-8")
    return index_path


def load_system_prompt() -> str:
    """Load the system prompt from SYSTEM.md."""
    return load_template("SYSTEM")


def load_update_prompt(current_time: str, current_index: str) -> str:
    """
    Load and format the update prompt with current values.

    Args:
        current_time: Current timestamp string
        current_index: Current GPT20 index content or empty message

    Returns:
        Formatted update prompt
    """
    return format_template("UPDATE_PROMPT", current_time=current_time, current_index=current_index)
