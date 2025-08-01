"""Template and index file utilities."""

from pathlib import Path
from string import Template


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


def read_index_for_update(index_name):
    index_path = _get_index_path(index_name)
    if index_path.exists():
        return index_path.read_text(encoding="utf-8"), True
    return "FILE IS EMPTY - CREATE THE INITIAL INDEX", False


def write_index(index_name, content):
    index_path = _get_index_path(index_name)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(content, encoding="utf-8")
    return index_path
