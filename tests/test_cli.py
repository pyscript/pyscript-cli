from __future__ import annotations

import unittest.mock
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Optional

import pytest
from mypy_extensions import VarArg
from typer.testing import CliRunner, Result

from pyscript import LATEST_PYSCRIPT_VERSION, __version__, config
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


def test_version() -> None:
    runner = CliRunner()
    result = runner.invoke(app, "--version")
    assert result.exit_code == 0
    assert f"PyScript CLI version: {__version__}" in result.stdout


@pytest.mark.parametrize("flag", ["-c", "--command"])
def test_wrap_command(invoke_cli: CLIInvoker, tmp_path: Path, flag: str) -> None:
    command = 'print("Hello World!")'
    result = invoke_cli("create", "--wrap", flag, command, "-o", "output.html")
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
    result = invoke_cli("create", "--wrap", *wrap_args)
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

    result = invoke_cli("create", str(input_file), "--wrap", *wrap_args)
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

    with unittest.mock.patch("pyscript.plugins.create.webbrowser.open") as browser_mock:
        result = invoke_cli("create", "--wrap", "--show", *args)

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


@pytest.mark.parametrize(
    "title, expected_title",
    [("test-title", "test-title"), (None, "PyScript App"), ("", "PyScript App")],
)
def test_wrap_title(
    invoke_cli: CLIInvoker,
    title: Optional[str],
    expected_title: str,
    tmp_path: Path,
) -> None:
    command = 'print("Hello World!")'
    args = ["create", "--wrap", "-c", command, "-o", "output.html"]
    if title is not None:
        args.extend(["--title", title])
    result = invoke_cli(*args)
    assert result.exit_code == 0

    expected_html_path = tmp_path / "output.html"
    assert expected_html_path.exists()

    with expected_html_path.open() as fp:
        html_text = fp.read()

    assert f"<py-script>\n{command}\n</py-script>" in html_text

    assert f"<title>{expected_title}</title>" in html_text


@pytest.mark.parametrize(
    "version, expected_version",
    [(None, LATEST_PYSCRIPT_VERSION), ("2022.9.1", "2022.9.1")],
)
def test_wrap_pyscript_version(
    invoke_cli: CLIInvoker,
    version: Optional[str],
    expected_version: str,
    tmp_path: Path,
) -> None:
    """
    Test that when wrap is called passing a string code input and an explicit pyscript version
    the project is created correctly
    """
    command = 'print("Hello World!")'
    args = ["create", "--wrap", "-c", command, "-o", "output.html"]
    if version is not None:
        args.extend(["--pyscript-version", version])

    # GIVEN a call to wrap with a cmd input and specific pyscript version as arguments
    result = invoke_cli(*args)
    assert result.exit_code == 0

    # EXPECT the output file to exist
    expected_html_path = tmp_path / "output.html"
    assert expected_html_path.exists()

    with expected_html_path.open() as fp:
        html_text = fp.read()

    # EXPECT the right cmd to be present in the output file
    assert f"<py-script>\n{command}\n</py-script>" in html_text

    # EXPECT the right JS and CSS version to be present in the output file
    version_str = (
        f'<script defer src="https://pyscript.net/releases/{expected_version}'
        '/pyscript.js"></script>'
    )
    css_version_str = (
        '<link rel="stylesheet" href="https://pyscript.net/releases/'
        f'{expected_version}/pyscript.css"/>'
    )
    assert version_str in html_text
    assert css_version_str in html_text


@pytest.mark.parametrize(
    "version, expected_version",
    [(None, LATEST_PYSCRIPT_VERSION), ("2022.9.1", "2022.9.1")],
)
def test_wrap_pyscript_version_file(
    invoke_cli: CLIInvoker,
    version: Optional[str],
    expected_version: str,
    tmp_path: Path,
) -> None:
    """
    Test that when wrap is called passing a file input and an explicit pyscript version
    the project is created correctly
    """
    command = 'print("Hello World!")'
    input_file = tmp_path / "hello.py"
    with input_file.open("w") as fp:
        fp.write(command)

    args = ["create", "--wrap", str(input_file), "-o", "output.html"]

    if version is not None:
        args.extend(["--pyscript-version", version])

    # GIVEN a call to wrap with a file and specific pyscript version as arguments
    result = invoke_cli(*args)
    assert result.exit_code == 0

    # EXPECT the output file to exist
    expected_html_path = tmp_path / "output.html"
    assert expected_html_path.exists()

    with expected_html_path.open() as fp:
        html_text = fp.read()

    # EXPECT the right cmd to be present in the output file
    assert f"<py-script>\n{command}\n</py-script>" in html_text

    # EXPECT the right JS and CSS version to be present in the output file
    version_str = (
        f'<script defer src="https://pyscript.net/releases/{expected_version}'
        '/pyscript.js"></script>'
    )
    css_version_str = (
        '<link rel="stylesheet" href="https://pyscript.net/releases/'
        f'{expected_version}/pyscript.css"/>'
    )
    assert version_str in html_text
    assert css_version_str in html_text


@pytest.mark.parametrize(
    "create_args, expected_version",
    [
        (("myapp1",), LATEST_PYSCRIPT_VERSION),
        (("myapp-w-version", "--pyscript-version", "2022.9.1"), "2022.9.1"),
    ],
)
def test_create_project_version(
    invoke_cli: CLIInvoker,
    tmp_path: Path,
    create_args: tuple[str],
    expected_version: str,
) -> None:
    """
    Test that project created with an explicit pyscript version are created correctly
    """
    command = 'print("Hello World!")'

    input_file = tmp_path / "hello.py"
    with input_file.open("w") as fp:
        fp.write(command)

    cmd_args = list(create_args) + [
        "--app-description",
        "tester-app",
        "--author-name",
        "tester",
        "--author-email",
        "tester@me.com",
    ]

    # GIVEN a call to wrap with a file and specific pyscript version as arguments
    result = invoke_cli("create", *cmd_args)
    assert result.exit_code == 0

    # EXPECT the app folder to exist
    expected_app_path = tmp_path / create_args[0]
    assert expected_app_path.exists()

    # EXPECT the app folder to contain the right index.html file
    app_file = expected_app_path / "index.html"
    assert app_file.exists()
    with app_file.open() as fp:
        html_text = fp.read()

    # EXPECT the right JS and CSS version to be present in the html file
    version_str = (
        f'<script defer src="https://pyscript.net/releases/{expected_version}'
        '/pyscript.js"></script>'
    )
    css_version_str = (
        '<link rel="stylesheet" href="https://pyscript.net/releases/'
        f'{expected_version}/pyscript.css"/>'
    )
    assert version_str in html_text
    assert css_version_str in html_text

    # EXPECT the folder to also contain the python main file
    py_file = expected_app_path / config["project_main_filename"]
    assert py_file.exists()

    # EXPECT the folder to also contain the config file
    config_file = expected_app_path / config["project_config_filename"]
    assert config_file.exists()
