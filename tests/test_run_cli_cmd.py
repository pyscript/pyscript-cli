from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest
from utils import CLIInvoker, invoke_cli  # noqa: F401

BASEPATH = str(Path(__file__).parent)


@pytest.mark.parametrize(
    "path",
    ["non_existing_folder", "non_existing_file.html"],
)
def test_run_bad_paths(invoke_cli: CLIInvoker, path: str):  # noqa: F811
    """
    Test that when wrap is called passing a bad path as input the command fails
    """
    # GIVEN a call to wrap with a bad path as argument
    result = invoke_cli("run", path)
    # EXPECT the command to fail
    assert result.exit_code == 1
    # EXPECT the right error message to be printed
    assert f"Error: Path {path} does not exist." in result.stdout


def test_run_server_bad_port(invoke_cli: CLIInvoker):  # noqa: F811
    """
    Test that when run is called passing a bad port as input the command fails
    """
    # GIVEN a call to run with a bad port as argument
    result = invoke_cli("run", "--port", "bad_port")
    # EXPECT the command to fail
    assert result.exit_code == 2
    # EXPECT the right error message to be printed
    assert "Error" in result.stdout
    assert (
        b"Invalid value for '--port': 'bad_port' is not a valid integer"
        in result.stdout_bytes
    )


@mock.patch("pyscript.plugins.run.start_server")
def test_run_server_with_default_values(
    start_server_mock, invoke_cli: CLIInvoker  # noqa: F811
):
    """
    Test that when run is called without arguments the command runs with the
    default values
    """
    # GIVEN a call to run without arguments
    result = invoke_cli("run")
    # EXPECT the command to succeed
    assert result.exit_code == 0
    # EXPECT start_server_mock function to be called with the default values:
    # Path("."): path to local folder
    # show=True: the opposite of the --silent option (which default to False)
    # port=8000: that is the default port
    start_server_mock.assert_called_once_with(Path("."), True, 8000)


@mock.patch("pyscript.plugins.run.start_server")
def test_run_server_with_silent_flag(
    start_server_mock, invoke_cli: CLIInvoker  # noqa: F811
):
    """
    Test that when run is called without arguments the command runs with the
    default values
    """
    # GIVEN a call to run without arguments
    result = invoke_cli("run", "--silent")
    # EXPECT the command to succeed
    assert result.exit_code == 0
    # EXPECT start_server_mock function to be called with the default values:
    # Path("."): path to local folder
    # show=False: the opposite of the --silent option
    # port=8000: that is the default port
    start_server_mock.assert_called_once_with(Path("."), False, 8000)


@pytest.mark.parametrize(
    "run_args, expected_values",
    [
        (("--silent",), (Path("."), False, 8000)),
        ((BASEPATH,), (Path(BASEPATH), True, 8000)),
        (("--port=8001",), (Path("."), True, 8001)),
        (("--silent", "--port=8001"), (Path("."), False, 8001)),
        ((BASEPATH, "--silent"), (Path(BASEPATH), False, 8000)),
        ((BASEPATH, "--port=8001"), (Path(BASEPATH), True, 8001)),
        ((BASEPATH, "--silent", "--port=8001"), (Path(BASEPATH), False, 8001)),
        ((BASEPATH, "--port=8001"), (Path(BASEPATH), True, 8001)),
    ],
)
@mock.patch("pyscript.plugins.run.start_server")
def test_run_server_with_valid_combinations(
    start_server_mock, invoke_cli: CLIInvoker, run_args, expected_values  # noqa: F811
):
    """
    Test that when run is called without arguments the command runs with the
    default values
    """
    # GIVEN a call to run without arguments
    result = invoke_cli("run", *run_args)
    # EXPECT the command to succeed
    assert result.exit_code == 0
    # EXPECT start_server_mock function to be called with the expected values
    start_server_mock.assert_called_once_with(*expected_values)
