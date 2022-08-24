"""
Tests for utility functions in the _generator.py module that cannot be
exercised because of limitations in the Typer testing framework (specifically,
multiple "prompt" arguments).
"""
from pathlib import Path
from typing import Any

import toml

from pyscript import _generator as gen


def test_create_project(tmp_cwd: Path, is_not_none: Any) -> None:
    app_name = "app_name"
    app_description = "A longer, human friendly, app description."
    author_name = "A.Coder"
    author_email = "acoder@domain.com"
    gen.create_project(app_name, app_description, author_name, author_email)

    manifest_path = tmp_cwd / app_name / "manifest.toml"
    assert manifest_path.exists()

    with manifest_path.open() as fp:
        contents = toml.load(fp)

    assert contents == {
        "app_name": "app_name",
        "app_description": "A longer, human friendly, app description.",
        "author_name": "A.Coder",
        "author_email": "acoder@domain.com",
        "created_on": is_not_none,
        "id": is_not_none,
        "version": is_not_none,
    }
