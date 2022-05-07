from __future__ import annotations

import unittest.mock
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Optional

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
    "wrap_args",
    [tuple(), ("-c", "print()", "script_name.py"), ("-c", "print()")],
    ids=["empty_args", "command_and_script", "command_no_output_or_show"],
)
def test_wrap_abort(invoke_cli: CLIInvoker, wrap_args: tuple[str]):
    result = invoke_cli("wrap", *wrap_args)
    assert result.exit_code == 1


@pytest.mark.parametrize(
    "wrap_args, expected_output_filename",
    [(("-o", "output.html"), "output.html"), (tuple(), "hello.html")],
)
def test_wrap_file(
    invoke_cli: CLIInvoker,
    tmp_path: Path,
    wrap_args: tuple[str],
    expected_output_filename: str,
) -> None:
    command = 'print("Hello World!")'

    input_file = tmp_path / "hello.py"
    with input_file.open("w") as fp:
        fp.write(command)

    result = invoke_cli("wrap", str(input_file), *wrap_args)
    assert result.exit_code == 0

    expected_html_path = tmp_path / expected_output_filename
    assert expected_html_path.exists()

    with expected_html_path.open() as fp:
        html_text = fp.read()

    assert f"<py-script>\n{command}\n</py-script>" in html_text


@pytest.mark.parametrize(
    "input_filename, additional_args, expected_output_filename",
    [
        ("hello.py", ("-o", "output.html"), "output.html"),
        ("hello.py", tuple(), None),
        (None, ("-c", 'print("Hello World!"'), None),
    ],
)
def test_wrap_show(
    invoke_cli: CLIInvoker,
    tmp_path: Path,
    input_filename: Optional[str],
    additional_args: tuple[str, ...],
    expected_output_filename: Optional[str],
) -> None:
    # TODO: Refactor this test

    # Generate an input file
    input_file: Optional[Path] = None
    if input_filename:
        input_file = tmp_path / input_filename
        with input_file.open("w") as fp:
            fp.write('print("Hello World!")')
        args = (str(input_file), *additional_args)
    else:
        args = additional_args

    with unittest.mock.patch("pyscript.cli.webbrowser.open") as browser_mock:
        result = invoke_cli("wrap", "--show", *args)

    assert result.exit_code == 0
    assert browser_mock.called

    should_be_deleted = False
    if expected_output_filename is None and input_filename is not None:
        assert input_file is not None
        expected_html_path = input_file.with_suffix(".html")
    elif expected_output_filename:
        expected_html_path = tmp_path / expected_output_filename
    else:
        expected_html_path = tmp_path / "pyscript_tmp.html"
        should_be_deleted = True

    browser_mock.assert_called_with(f"file://{expected_html_path.resolve()}")

    if not should_be_deleted:
        assert expected_html_path.exists()
    else:
        assert not expected_html_path.exists()


@pytest.mark.parametrize("title, expected_title", [("test-title", "test-title"), (None, "PyScript App")])
def test_wrap_title(
    invoke_cli: CLIInvoker,
    title: str,
    expected_title: str,
    tmp_path: Path,
) -> None:
    command = 'print("Hello World!")'
    result = invoke_cli("wrap", "-c", command, "-o", "output.html", "--title", title)
    assert result.exit_code == 0

    expected_html_path = tmp_path / "output.html"
    assert expected_html_path.exists()

    with expected_html_path.open() as fp:
        html_text = fp.read()

    assert f"<py-script>\n{command}\n</py-script>" in html_text

    assert f"<title>{expected_title}</title>" in html_text