from pathlib import Path
from typing import Optional

import jinja2

_cwd_loader = jinja2.FileSystemLoader(Path.cwd().resolve())
_package_loader = jinja2.PackageLoader("pyscript")
_env = jinja2.Environment(loader=jinja2.ChoiceLoader([_cwd_loader, _package_loader]))


def string_to_html(
    input_str: str, title: str, template_name: Optional[str], output_path: Path
) -> None:
    """Write a Python script string to an HTML file template."""
    template_name = template_name or "basic.html"
    template = _env.get_template(template_name)
    with output_path.open("w") as fp:
        fp.write(template.render(code=input_str, title=title))


def file_to_html(
    input_path: Path,
    title: str,
    template_name: Optional[str],
    output_path: Optional[Path],
) -> None:
    """Write a Python script string to an HTML file template."""
    output_path = output_path or input_path.with_suffix(".html")
    with input_path.open("r") as fp:
        string_to_html(fp.read(), title, template_name, output_path)
