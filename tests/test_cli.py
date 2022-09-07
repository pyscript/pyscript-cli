from __future__ import annotations

import unittest.mock
from collections.abc import Sequence
from dataclasses import dataclass
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


@dataclass
class Dependency:
    """Data class to encapsulate code dependency dynamically injected in code under test.
    This class is a general abstraction over both external and local module dependency."""

    import_line: str  # Import line to inject in code under test
    filename: str | None = (
        None  # filename: to be used for tmp local modules, i.e. paths
    )
    code: str | None = None  # code in the tmp local modules
    inject: str | None = None  # any code to inject in code under test


@pytest.fixture()
def invoke_cli(tmp_path: Path, monkeypatch: "MonkeyPatch") -> CLIInvoker:
    """Returns a function, which can be used to call the CLI from within a temporary directory."""
    runner = CliRunner()

    monkeypatch.chdir(tmp_path)

    def f(*args: str) -> Result:
        return runner.invoke(app, args)

    return f


@pytest.fixture()
def py_code() -> str:
    pycode = """
from math import sqrt


def square_root(number: int) -> float:
    return sqrt(number)


print(f"Square root of 25 is {square_root(25)}")
    """
    return pycode


@pytest.fixture()
def py_code_with_import() -> str:
    pycode = """
import numpy as np

from sklearn.datasets import load_iris

SEED = 12345
np.random.seed(SEED)
iris = load_iris()
    """
    return pycode


def test_version() -> None:
    runner = CliRunner()
    result = runner.invoke(app, "--version")
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
    py_code: str,
    wrap_args: tuple[str],
    expected_output_filename: str,
) -> None:

    input_file = tmp_path / "hello.py"
    with input_file.open("w") as fp:
        fp.write(py_code)

    result = invoke_cli("wrap", str(input_file), *wrap_args)
    assert result.exit_code == 0

    expected_html_path = tmp_path / expected_output_filename
    assert expected_html_path.exists()

    with expected_html_path.open() as fp:
        html_text = fp.read()

    assert f"<py-script>\n{py_code}\n</py-script>" in html_text


@pytest.mark.parametrize(
    "dependencies, expected_warnings",
    [
        (None, False),
        (
            (
                Dependency(
                    filename="preprocessor.py",
                    code="from sklearn.preprocessing import StandardScaler\n "
                    "scaler = StandardScaler()",
                    import_line="from preprocessor import scaler",
                    inject="scaler.fit(iris.data)",
                ),
            ),
            False,
        ),
        (
            (
                Dependency(
                    filename="preprocessor.py",
                    code="from sklearn.preprocessing import StandardScaler\n "
                    "scaler = StandardScaler()",
                    import_line="import preprocessor",
                    inject="preprocessor.scaler.fit(iris.data)",
                ),
            ),
            False,
        ),
        (
            (
                Dependency(
                    import_line="from umap import UMAP",
                ),
            ),
            True,
        ),
    ],
)
def test_wrap_file_with_imports(
    invoke_cli: CLIInvoker,
    tmp_path: Path,
    py_code_with_import,
    dependencies: Optional[Sequence[Dependency]],
    expected_warnings: bool,
) -> None:

    # A. Inject code dependencies, if any
    if dependencies:
        # inject dependency
        for dep in dependencies:
            if dep.filename and dep.code:
                tmp_mod = tmp_path / dep.filename
                with tmp_mod.open("w") as fp:
                    fp.write(dep.code)
            # inject import line in code under test
            py_code_with_import = dep.import_line + py_code_with_import
            if dep.inject:
                py_code_with_import += (
                    "\n" + dep.inject
                )  # append code to inject to code under test

    input_file = tmp_path / "ml.py"
    with input_file.open("w") as fp:
        fp.write(py_code_with_import)

    result = invoke_cli("wrap", str(input_file))
    assert result.exit_code == 0
    if expected_warnings:
        assert "WARNING" in result.stdout
    else:
        assert "WARNING" not in result.stdout

    expected_html_path = tmp_path / "ml.html"
    assert expected_html_path.exists()

    with expected_html_path.open() as fp:
        html_text = fp.read()

    assert f"<py-script>\n{py_code_with_import}\n</py-script>" in html_text
    assert "<py-env>" in html_text and "</py-env>" in html_text

    # get pyenv_tag content
    pyenv_tag = html_text[html_text.find("<py-env>") : html_text.find("</py-env>")]
    pyscript_tag = html_text[
        html_text.find("<py-script>") : html_text.find("</py-script>")
    ]

    # default py-env dependency in fixture code
    assert "numpy" in pyenv_tag
    assert "scikit-learn" in pyenv_tag

    if dependencies:
        for dep in dependencies:
            if dep.filename:
                assert "paths" in pyenv_tag
                assert dep.filename in pyenv_tag
            assert dep.import_line in py_code_with_import
            assert dep.import_line in pyscript_tag
            if dep.inject:
                assert dep.inject in pyscript_tag
                assert dep.inject in py_code_with_import


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
    py_code: str,
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
            fp.write(py_code)
        args = (str(input_file), *additional_args)
    else:
        args = additional_args

    with unittest.mock.patch("pyscript.plugins.wrap.webbrowser.open") as browser_mock:
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


@pytest.mark.parametrize(
    "title, expected_title",
    [("test-title", "test-title"), (None, "PyScript App"), ("", "PyScript App")],
)
def test_wrap_title(
    invoke_cli: CLIInvoker,
    py_code: str,
    title: Optional[str],
    expected_title: str,
    tmp_path: Path,
) -> None:
    command = py_code
    args = ["wrap", "-c", py_code, "-o", "output.html"]
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
