from pathlib import Path

import jinja2

_env = jinja2.Environment(loader=jinja2.PackageLoader("pyscript"))


def string_to_html(input_str: str, output_path: Path) -> None:
    """Write a Python script string to an HTML file template."""
    template = _env.get_template("basic.html")
    with output_path.open("w") as fp:
        fp.write(template.render(code=input_str))


def file_to_html(input_path: Path, output_path: Path) -> None:
    """Write a Python script string to an HTML file template."""
    with input_path.open("r") as fp:
        string_to_html(fp.read(), output_path)
