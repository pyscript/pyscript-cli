import json
from pathlib import Path
from typing import Optional

import jinja2
import requests
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
    pyscript_version: str,
    template: str = "basic.html",
) -> None:
    """Write a Python script string to an HTML file template.


    Params:
        - title (str): application title, that will be placed as title of the html
        - python_file_path (str): path to the python file to be loaded by the app
        - config_file_path (str): path to the config file to be loaded by the app
        - output_file_path (Path): path where to write the new html file
        - pyscript_version (str): version of pyscript to be used
        - template (str): name of the template to be used

    Output:
        (None)
    """
    template_instance = _env.get_template(template)

    with output_file_path.open("w") as fp:
        fp.write(
            template_instance.render(
                python_file_path=python_file_path,
                config_file_path=config_file_path,
                title=title,
                pyscript_version=pyscript_version,
            )
        )


def save_config_file(config_file: Path, configuration: dict):
    """Write an app configuration dict to `config_file`.

    Params:

        - config_file(Path): path configuration file. (i.e.: "pyscript.toml"). Supported
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


def create_project(
    app_or_file_name: Optional[str],
    app_description: str,
    author_name: str,
    author_email: str,
    pyscript_version: Optional[str] = None,
    project_type: str = "app",
    wrap: bool = False,
    command: Optional[str] = None,
    output: Optional[str] = None,
) -> None:
    """
    New files created:

    pyscript.toml - project metadata and config file
    main.py - a "Hello world" python starter module
    index.html - start page for the project
    """

    if wrap:
        if command:
            # app_or_file_name is None in this case
            assert app_or_file_name is None
            if output:
                app_name = output.removesuffix(".html")
            else:
                app_name = "pyscript-command-app"
        else:
            assert app_or_file_name is not None
            app_name = app_or_file_name.removesuffix(".py")
    else:
        if app_or_file_name and app_or_file_name.endswith(".py"):
            app_name = app_or_file_name.removesuffix(".py")
        else:
            # At this point we should always have a name, but typing
            # was complaining so let's add a default
            app_name = app_or_file_name or "my-pyscript-app"

    if not pyscript_version:
        pyscript_version = _get_latest_pyscript_version()

    if project_type == "app":
        template = "basic.html"
    else:
        raise ValueError(
            f"Unknown project type: {project_type}. Valid values are: 'app'"
        )

    context = {
        "name": app_name,
        "description": app_description,
        "type": project_type,
        "author_name": author_name,
        "author_email": author_email,
        "version": "latest",
    }

    app_dir = Path(".") / app_name
    app_dir.mkdir()
    manifest_file = app_dir / config["project_config_filename"]

    save_config_file(manifest_file, context)
    output_path = app_dir / "index.html" if output is None else app_dir / output

    python_filepath = app_dir / "main.py"

    if not wrap:
        if app_or_file_name and app_or_file_name.endswith(".py"):
            python_filepath.write_bytes(Path(app_or_file_name).read_bytes())
        else:
            # Save the new python file
            with python_filepath.open("w", encoding="utf-8") as fp:
                fp.write(TEMPLATE_PYTHON_CODE)
    else:
        if command:
            with python_filepath.open("w", encoding="utf-8") as fp:
                fp.write(command)
        else:
            assert app_or_file_name is not None
            python_filepath.write_bytes(Path(app_or_file_name).read_bytes())

    create_project_html(
        app_name,
        config["project_main_filename"],
        config["project_config_filename"],
        output_path,
        pyscript_version=pyscript_version,
        template=template,
    )


def _get_latest_pyscript_version() -> str:
    """Get the latest version of PyScript from GitHub."""
    url = "https://api.github.com/repos/pyscript/pyscript/releases/latest"
    try:
        response = requests.get(url)

        if not response.ok:
            pyscript_version = LATEST_PYSCRIPT_VERSION
        else:

            data = response.json()
            pyscript_version = data["tag_name"]
    except Exception:
        pyscript_version = LATEST_PYSCRIPT_VERSION

    return pyscript_version
