from pathlib import Path
from typing import Optional

import jinja2

from ._node_parser import find_imports, FinderResult
from ._node_parser import _convert_notebook


class UnsupportedFileType(Exception):
    pass


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

    fname, extension = input_path.name, input_path.suffix
    if extension == ".py":
        with open(input_path, "rt") as f:
            source = f.read()

    elif extension == ".ipynb":
        try:
            import nbconvert
        except ImportError as e:  # pragma no cover
            raise ImportError(
                "Please install nbconvert to serve Jupyter Notebooks."
            ) from e
        source = _convert_notebook(input_path)

    else:
        raise UnsupportedFileType(
            "{} is neither a script (.py) nor a notebook (.ipynb)".format(fname)
        )

    import_results = find_imports(source, input_path)
    with input_path.open("r") as fp:
        string_to_html(source, title, output_path, pyenv=import_results)
    if import_results.has_warnings:
        return import_results


def create_project(
    app_name: str,
    app_description: str,
    author_name: str,
    author_email: str,
) -> None:
    """
    New files created:

    manifest.toml - project metadata
    index.html - a "Hello world" start page for the project.

    TODO: more files to add to the core project start state.
    """
    context = {
        "name": app_name,
        "description": app_description,
        "type": "app",
        "author_name": author_name,
        "author_email": author_email,
        "version": f"{datetime.date.today().year}.1.1",
        "created_on": datetime.datetime.now(),
    }
    app_dir = Path(".") / app_name
    app_dir.mkdir()
    manifest_file = app_dir / "manifest.toml"
    with manifest_file.open("w", encoding="utf-8") as fp:
        toml.dump(context, fp)
    index_file = app_dir / "index.html"
    string_to_html('print("Hello, world!")', app_name, index_file)
