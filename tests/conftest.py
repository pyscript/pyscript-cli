from pathlib import Path
from typing import Any

import pytest
from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture
def auto_enter(monkeypatch):
    """
    Monkey patch 'typer.confirm' to always hit <Enter>".
    """

    def user_hit_enter(*args, **kwargs):
        return ""

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
