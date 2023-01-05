"""
Tests for utility functions in the _generator.py module that cannot be
exercised because of limitations in the Typer testing framework (specifically,
multiple "prompt" arguments).
"""
import json
from pathlib import Path
from typing import Any
import toml

import pytest

from pyscript import _generator as gen
from pyscript import config


def test_create_project(tmp_cwd: Path, is_not_none: Any) -> None:
    app_name = "app_name"
    app_description = "A longer, human friendly, app description."
    author_name = "A.Coder"
    author_email = "acoder@domain.com"

    # GIVEN a a new project
    gen.create_project(app_name, app_description, author_name, author_email)

    # with a default config path
    manifest_path = tmp_cwd / app_name / config["project_config_filename"]

    # assert that the new project config file exists
    assert manifest_path.exists()

    # assert that we can load it as a TOML file (TOML is the default config format)
    # and that the contents of the config are as we expect
    with manifest_path.open() as fp:
        contents = toml.load(fp)

    assert contents == {
        "name": "app_name",
        "description": "A longer, human friendly, app description.",
        "type": "app",
        "author_name": "A.Coder",
        "author_email": "acoder@domain.com",
        "version": is_not_none,
    }


def test_create_project_twice_raises_error(tmp_cwd: Path) -> None:
    """We get a FileExistsError when we try to create an existing project."""
    app_name = "app_name"
    app_description = "A longer, human friendly, app description."
    author_name = "A.Coder"
    author_email = "acoder@domain.com"
    gen.create_project(app_name, app_description, author_name, author_email)

    with pytest.raises(FileExistsError):
        gen.create_project(app_name, app_description, author_name, author_email)


def test_create_project_explicit_json(tmp_cwd: Path, is_not_none: Any, monkeypatch) -> None:
    app_name = "JSON_app_name"
    app_description = "A longer, human friendly, app description."
    author_name = "A.Coder"
    author_email = "acoder@domain.com"

    # Let's patch the config so that the project config file is a JSON file
    config_file_name = 'pyscript.json'
    monkeypatch.setitem(gen.config, 'project_config_filename', config_file_name)

    # GIVEN a new project
    gen.create_project(app_name, app_description, author_name, author_email)

    # get the path where the config file is being created
    manifest_path = tmp_cwd / app_name / config["project_config_filename"]

    # assert that the new project config file exists
    assert manifest_path.exists()

    # assert that we can load it as a TOML file (TOML is the default config format)
    # and that the contents of the config are as we expect
    with manifest_path.open() as fp:
        contents = json.load(fp)

    assert contents == {
        "name": "JSON_app_name",
        "description": app_description,
        "type": "app",
        "author_name": author_name,
        "author_email": author_email,
        "version": is_not_none,
    }


def test_create_project_explicit_toml(tmp_cwd: Path, is_not_none: Any, monkeypatch) -> None:
    app_name = "TOML_app_name"
    app_description = "A longer, human friendly, app description."
    author_name = "A.Coder"
    author_email = "acoder@domain.com"

    # Let's patch the config so that the project config file is a JSON file
    config_file_name = 'mypyscript.toml'
    monkeypatch.setitem(gen.config, 'project_config_filename', config_file_name)

    # GIVEN a new project
    gen.create_project(app_name, app_description, author_name, author_email)

    # get the path where the config file is being created
    manifest_path = tmp_cwd / app_name / config["project_config_filename"]

    check_project_manifest(manifest_path, toml, app_name, is_not_none)

def check_project_manifest(
    config_path: Path, serializer: Any, app_name: str, is_not_none: Any,
    app_description: str = "A longer, human friendly, app description.",
    author_name: str = "A.Coder", author_email: str = "acoder@domain.com",
    project_type: str = "app"):
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

    assert contents == {
        "name": app_name,
        "description": app_description,
        "type": project_type,
        "author_name": author_name,
        "author_email": author_email,
        "version": is_not_none,
    }
