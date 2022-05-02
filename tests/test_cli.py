from pathlib import Path
from typing import TYPE_CHECKING, Callable

import pytest
from mypy_extensions import VarArg
from typer.testing import CliRunner, Result

from pyscript import __version__
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


@pytest.mark.parametrize("cli_arg", ["version", "--version"])
def test_version(invoke_cli: CLIInvoker, cli_arg: str) -> None:
    result = invoke_cli(cli_arg)
    assert result.exit_code == 0
    assert f"PyScript CLI version: {__version__}" in result.stdout


@pytest.mark.parametrize("flag", ["-c", "--command"])
def test_wrap_command(invoke_cli: CLIInvoker, tmp_path: Path, flag: str) -> None:
    command = 'print("Hello World!")'
    result = invoke_cli("wrap", flag, command, "-o", "output.html")
    assert result.exit_code == 0

    expected_html_path = tmp_path / "output.html"
    assert expected_html_path.exists()

    with expected_html_path.open() as fp:
        html_text = fp.read()

    assert f"<py-script>\n{command}\n</py-script>" in html_text


@pytest.mark.parametrize(
    "extra_args, expected_output_filename",
    [(("-o", "output.html"), "output.html"), (tuple(), "hello.html")],
)
def test_wrap_file(
    invoke_cli: CLIInvoker,
    tmp_path: Path,
    extra_args: tuple[str],
    expected_output_filename: str,
) -> None:
    command = 'print("Hello World!")'

    input_file = tmp_path / "hello.py"
    with input_file.open("w") as fp:
        fp.write(command)

    result = invoke_cli("wrap", str(input_file), *extra_args)
    assert result.exit_code == 0

    expected_html_path = tmp_path / expected_output_filename
    assert expected_html_path.exists()

    with expected_html_path.open() as fp:
        html_text = fp.read()

    assert f"<py-script>\n{command}\n</py-script>" in html_text
