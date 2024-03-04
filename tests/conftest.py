from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from _pytest.monkeypatch import MonkeyPatch

from pyscript import LATEST_PYSCRIPT_VERSION


@pytest.fixture(scope="session", autouse=True)
def requests():
    mocked_result = {"tag_name": LATEST_PYSCRIPT_VERSION}

    with patch("pyscript._generator.requests") as mocked_requests:
        mocked_get = MagicMock()
        mocked_get.ok = True
        mocked_get.json = MagicMock(return_value=mocked_result)
        mocked_requests.get.return_value = mocked_get
        yield mocked_requests


@pytest.fixture
def auto_enter(monkeypatch):
    """
    Monkey patch 'typer.prompt' to always hit <Enter>".
    """

    def user_hit_enter(*args, **kwargs):
        # This makes sure that if there is a default value on a prompt
        # we will return it, otherwise we will return an empty string
        # which isn't the same as hitting enter!
        default_value = kwargs.get("default", "")
        return default_value

    monkeypatch.setattr("typer.prompt", user_hit_enter)


@pytest.fixture()
def tmp_cwd(monkeypatch: MonkeyPatch, tmp_path: Path) -> Path:
    """Create & return a temporary directory after setting current working directory to it."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture(scope="session")
def is_not_none() -> Any:
    """
    An object that can be used to test whether another is None.

    This is particularly useful when testing contents of collections, e.g.:

    ```python
    def test_data(data, is_not_none):
        assert data == {"some_key": is_not_none, "some_other_key": 5}
    ```

    """

    class _NotNone:
        def __eq__(self, other):
            return other is not None

    return _NotNone()
