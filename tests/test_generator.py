"""
Tests for utility functions in the _generator.py module that cannot be
exercised because of limitations in the Typer testing framework (specifically,
multiple "prompt" arguments).
"""
from unittest import mock

from pyscript import _generator as gen


def test_create_project() -> None:
    gen.toml = mock.MagicMock()
    mock_path = mock.MagicMock()
    mock_path.__truediv__ = mock.MagicMock(return_value=mock_path)
    gen.Path = mock.MagicMock(return_value=mock_path)  # type: ignore
    gen.string_to_html = mock.MagicMock()
    app_name = "app_name"
    app_description = "A longer, human friendly, app description."
    author_name = "A.Coder"
    author_email = "acoder@domain.com"
    gen.create_project(app_name, app_description, author_name, author_email)
    assert gen.toml.dump.call_count == 1  # type: ignore
    gen.string_to_html.assert_called_once_with(  # type: ignore
        'print("Hello, world!")', app_name, mock_path
    )
