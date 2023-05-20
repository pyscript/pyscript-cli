from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable

import pytest
from mypy_extensions import VarArg
from typer.testing import CliRunner, Result

from pyscript.cli import app

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch

CLIInvoker = Callable[[VarArg(str)], Result]


@pytest.fixture()
def invoke_cli(tmp_path: Path, monkeypatch: "MonkeyPatch") -> CLIInvoker:
    """Returns a function, which can be used to call the CLI from within a temporary directory."""
    runner = CliRunner()

    monkeypatch.chdir(tmp_path)

    def f(*args: str) -> Result:
        return runner.invoke(app, args)

    return f
