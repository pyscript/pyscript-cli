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
