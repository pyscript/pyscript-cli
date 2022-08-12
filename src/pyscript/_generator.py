from pathlib import Path
from typing import Optional

import jinja2

from ._node_parser import find_imports, FinderResult

_env = jinja2.Environment(
    loader=jinja2.PackageLoader("pyscript"), trim_blocks=True, lstrip_blocks=True
)


def string_to_html(
    input_str: str, title: str, output_path: Path, pyenv: FinderResult = None
) -> None:
    """Write a Python script string to an HTML file template."""
    template = _env.get_template("basic.html")
    if pyenv is not None:
        modules, paths = pyenv.packages, pyenv.paths
    else:
        modules = paths = ()
    with output_path.open("w") as fp:
        fp.write(
            template.render(code=input_str, title=title, modules=modules, paths=paths)
        )


def file_to_html(
    input_path: Path, title: str, output_path: Optional[Path]
) -> Optional[FinderResult]:
    """Write a Python script string to an HTML file template.

    Warnings will be returned when scanning for environment, if any.
    """
    output_path = output_path or input_path.with_suffix(".html")
    import_results = find_imports(input_path)
    with input_path.open("r") as fp:
        string_to_html(fp.read(), title, output_path, pyenv=import_results)
    if import_results.has_warnings:
        return import_results
