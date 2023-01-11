import datetime
import json
from pathlib import Path
from typing import Optional

import jinja2
import toml

from pyscript import LATEST_PYSCRIPT_VERSION, config

_env = jinja2.Environment(loader=jinja2.PackageLoader("pyscript"))
TEMPLATE_PYTHON_CODE = """# Replace the code below with your own
print("Hello, world!")
"""


def create_project_html(
    title: str,
    python_file_path: str,
    config_file_path: str,
    output_file_path: Path,
    pyscript_version: str = LATEST_PYSCRIPT_VERSION,
) -> None:
    """Write a Python script string to an HTML file template."""
    template = _env.get_template("basic.html")
    with output_file_path.open("w") as fp:
        fp.write(
            template.render(
                python_file_path=python_file_path,
                config_file_path=config_file_path,
                title=title,
                pyscript_version=pyscript_version,
            )
        )


def save_config_file(config_file: Path, configuration: dict):
    """Write an app configuration dict to `config_file`.

    Params:

     - config_file(Path): path configuration file. (I.e.: "pyscript.toml"). Supported
                          formats: `toml` and `json`.
     - configuration(dict): app configuration to be saved

    Return:
        (None)
    """
    with config_file.open("w", encoding="utf-8") as fp:
        if str(config_file).endswith(".json"):
            json.dump(configuration, fp)
        else:
            toml.dump(configuration, fp)


def string_to_html(
    code: str,
    title: str,
    output_path: Path,
    template_name: str = "basic.html",
    pyscript_version: str = LATEST_PYSCRIPT_VERSION,
) -> None:
    """Write a Python script string to an HTML file template.

    Params:

        - code(str): string containing the application code to be written to the
                     PyScript app template
        - title(str): application title, that will be placed as title of the html
                      app template
        - output_path(Path): path where to write the new html file
        - template_name(str): name of the template to be used
        - pyscript_version(str): version of pyscript to be used

    Output:
        (None)
    """
    template = _env.get_template(template_name)
    with output_path.open("w") as fp:
        fp.write(
            template.render(code=code, title=title, pyscript_version=pyscript_version)
        )


def file_to_html(
    input_path: Path,
    title: str,
    output_path: Optional[Path],
    template_name: str = "basic.html",
    pyscript_version: str = LATEST_PYSCRIPT_VERSION,
) -> None:
    """Write a Python script string to an HTML file template."""
    output_path = output_path or input_path.with_suffix(".html")
    with input_path.open("r") as fp:
        string_to_html(fp.read(), title, output_path, template_name, pyscript_version)


def create_project(
    app_name: str,
    app_description: str,
    author_name: str,
    author_email: str,
    pyscript_version: str = LATEST_PYSCRIPT_VERSION,
) -> None:
    """
    New files created:

    pyscript.json - project metadata
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
    }
    app_dir = Path(".") / app_name
    app_dir.mkdir()
    manifest_file = app_dir / config["project_config_filename"]
    with manifest_file.open("w", encoding="utf-8") as fp:
        if str(manifest_file).endswith(".json"):
            json.dump(context, fp)
        else:
            toml.dump(context, fp)

    index_file = app_dir / "index.html"

    # Save the new python file
    python_filepath = app_dir / "main.py"
    with python_filepath.open("w", encoding="utf-8") as fp:
        fp.write(TEMPLATE_PYTHON_CODE)

    create_project_html(
        app_name,
        config["project_main_filename"],
        config["project_config_filename"],
        index_file,
    )
