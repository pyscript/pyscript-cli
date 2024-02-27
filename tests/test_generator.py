"""
Tests for utility functions in the _generator.py module that cannot be
exercised because of limitations in the Typer testing framework (specifically,
multiple "prompt" arguments).
"""

import json
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
import toml

from pyscript import _generator as gen
from pyscript import config

TESTS_AUTHOR_NAME = "A.Coder"
TESTS_AUTHOR_EMAIL = "acoder@domain.com"


def test_create_app(tmp_cwd: Path, is_not_none: Any) -> None:
    """
    Test that a new app is created with the correct files and manifest.
    """
    app_name = "app_name"
    app_description = "A longer, human friendly, app description."

    # GIVEN a a new project
    gen.create_project(app_name, app_description, TESTS_AUTHOR_NAME, TESTS_AUTHOR_EMAIL)

    # with a default config path
    manifest_path = tmp_cwd / app_name / config["project_config_filename"]

    check_project_manifest(manifest_path, toml, app_name, is_not_none)
    check_project_files(tmp_cwd / app_name)


def test_create_bad_type(tmp_cwd: Path, is_not_none: Any) -> None:
    """
    Test that a new project with a bad type raises a ValueError
    """
    app_name = "app_name"
    app_description = "A longer, human friendly, app description."

    # GIVEN a a new project with a bad type assert it raises a
    with pytest.raises(ValueError):
        gen.create_project(
            app_name,
            app_description,
            TESTS_AUTHOR_NAME,
            TESTS_AUTHOR_EMAIL,
            project_type="bad_type",
        )


def test_create_project_twice_raises_error(tmp_cwd: Path) -> None:
    """We get a FileExistsError when we try to create an existing project."""
    app_name = "app_name"
    app_description = "A longer, human friendly, app description."
    gen.create_project(app_name, app_description, TESTS_AUTHOR_NAME, TESTS_AUTHOR_EMAIL)

    with pytest.raises(FileExistsError):
        gen.create_project(
            app_name, app_description, TESTS_AUTHOR_NAME, TESTS_AUTHOR_EMAIL
        )


def test_create_project_explicit_json(
    tmp_cwd: Path, is_not_none: Any, monkeypatch
) -> None:
    app_name = "JSON_app_name"
    app_description = "A longer, human friendly, app description."

    # Let's patch the config so that the project config file is a JSON file
    config_file_name = "pyscript.json"
    monkeypatch.setitem(gen.config, "project_config_filename", config_file_name)

    # GIVEN a new project
    gen.create_project(app_name, app_description, TESTS_AUTHOR_NAME, TESTS_AUTHOR_EMAIL)

    # get the path where the config file is being created
    manifest_path = tmp_cwd / app_name / config["project_config_filename"]

    check_project_manifest(manifest_path, json, app_name, is_not_none)


def test_create_project_explicit_toml(
    tmp_cwd: Path, is_not_none: Any, monkeypatch
) -> None:
    app_name = "TOML_app_name"
    app_description = "A longer, human friendly, app description."

    # Let's patch the config so that the project config file is a JSON file
    config_file_name = "mypyscript.toml"
    monkeypatch.setitem(gen.config, "project_config_filename", config_file_name)

    # GIVEN a new project
    gen.create_project(app_name, app_description, TESTS_AUTHOR_NAME, TESTS_AUTHOR_EMAIL)

    # get the path where the config file is being created
    manifest_path = tmp_cwd / app_name / config["project_config_filename"]

    check_project_manifest(manifest_path, toml, app_name, is_not_none)


def check_project_manifest(
    config_path: Path,
    serializer: Any,
    app_name: str,
    is_not_none: Any,
    app_description: str = "A longer, human friendly, app description.",
    author_name: str = TESTS_AUTHOR_NAME,
    author_email: str = TESTS_AUTHOR_EMAIL,
    project_type: str = "app",
):
    """
    Perform the following:

        * checks that `config_path` exists
        * loads the contents of `config_path` using `serializer.load`
        * check that the contents match with the values provided in input. Specifically:
            * "name" == app_name
            * "description" == app_description
            * "type" == app_type
            * "author_name" == author_name
            * "author_email" == author_email
            * "version" == is_not_none

    Params:
        * config_path(Path): path to the app config file
        * serializer(json|toml): serializer to be used to load contents of `config_path`.
                                 Supported values are either modules `json` or `toml`
        * app_name(str): name of application
        * is_not_none(any): pytest fixture
        * app_description(str): application description
        * author_name(str): application author name
        * author_email(str): application author email
        * project_type(str): project type

    """
    # assert that the new project config file exists
    assert config_path.exists()

    # assert that we can load it as a TOML file (TOML is the default config format)
    # and that the contents of the config are as we expect
    with config_path.open() as fp:
        contents = serializer.load(fp)

    expected = {
        "name": app_name,
        "description": app_description,
        "type": project_type,
        "author_name": author_name,
        "author_email": author_email,
        "version": is_not_none,
    }
    assert contents == expected


def check_project_files(
    app_folder: Path,
    html_file: str = "index.html",
    config_file: str = config["project_config_filename"],
    python_file: str = "main.py",
):
    """
    Perform the following checks:

        * checks that app_folder/html_file exists
        * checks that app_folder/config_file exists
        * checks that app_folder/python_file exists
        * checks that html_file actually loads both the python and the config files

    Params:
        * config_path(Path): path to the app folder
        * html_file(str): name of the html file generated by the template
                          (default: index.html)
        * config_file(str): name of the config file generated by the template
                          (default: config["project_config_filename"])
        * python_file(str): name of the python file generated by the template
                          (default: main.py)

    """
    # assert that the new project files exists
    html_file_path = app_folder / html_file
    assert html_file_path.exists(), f"{html_file} not found! :("
    assert (app_folder / config_file).exists(), f"{config_file} not found! :("
    assert (app_folder / python_file).exists(), f"{python_file} not found! :("

    with html_file_path.open() as fp:
        contents = fp.read()
        assert (
            f'<script type="py" src="./{python_file}" config="./{config_file}">'
            in contents
        )


def check_plugin_project_files(
    app_folder: Path,
    plugin_name: str,
    plugin_description: str,
    html_file: str = "index.html",
    config_file: str = config["project_config_filename"],
    python_file: str = "main.py",
):
    """
    Perform the following checks:

        * checks that app_folder/html_file exists
        * checks that app_folder/config_file exists
        * checks that app_folder/python_file exists
        * checks that html_file actually loads both the python and the config files
        * checks that app_folder/html_file contains the right html page documenting
          the plugin, according to the plugin template

    Params:
        * config_path(Path): path to the app folder
        * html_file(str): name of the html file generated by the template
                          (default: index.html)
        * config_file(str): name of the config file generated by the template
                          (default: config["project_config_filename"])
        * python_file(str): name of the python file generated by the template
                          (default: main.py)

    """
    # assert that the new project files exists
    html_file_path = app_folder / html_file
    assert html_file_path.exists(), f"{html_file} not found! :("
    assert (app_folder / config_file).exists(), f"{config_file} not found! :("
    assert (app_folder / python_file).exists(), f"{python_file} not found! :("

    with html_file_path.open() as fp:
        contents = fp.read()
        contents = dedent(contents)
        assert f"            <h1>{plugin_name}</h1>" in contents
        assert dedent(
            f"""        <div>
            <h2> Description </h2>
            <p>{ plugin_description }</p>
        </div>"""
        )
        assert f'<py-script src="./{python_file}">' in contents
        assert f'<py-config src="./{config_file}">' in contents
