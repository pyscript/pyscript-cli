from __future__ import annotations

import http.client
import http.server
import threading
from pathlib import Path
from unittest import mock

import pytest
from utils import CLIInvoker, invoke_cli  # noqa: F401

from pyscript.plugins.run import get_folder_based_http_request_handler

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
    assert "'bad_port' is not a valid integer" in result.stdout


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
    # show=True: same as passing the --view option (which defaults to True)
    # port=8000: that is the default port
    # default_file=None: default behavior is to have no default file
    start_server_mock.assert_called_once_with(Path("."), True, 8000, default_file=None)


@mock.patch("pyscript.plugins.run.start_server")
def test_run_server_with_no_view_flag(
    start_server_mock, invoke_cli: CLIInvoker  # noqa: F811
):
    """
    Test that when run is called without arguments the command runs with the
    default values
    """
    # GIVEN a call to run without arguments
    result = invoke_cli("run", "--no-view")
    # EXPECT the command to succeed
    assert result.exit_code == 0
    # EXPECT start_server_mock function to be called with the default values:
    # Path("."): path to local folder
    # show=False: same as passing the --no-view option
    # port=8000: that is the default port
    # default_file=None: default behavior is to have no default file
    start_server_mock.assert_called_once_with(Path("."), False, 8000, default_file=None)


@pytest.mark.parametrize(
    "run_args, expected_posargs, expected_kwargs",
    [
        (("--no-view",), (Path("."), False, 8000), {"default_file": None}),
        ((BASEPATH,), (Path(BASEPATH), True, 8000), {"default_file": None}),
        (("--port=8001",), (Path("."), True, 8001), {"default_file": None}),
        (("--no-view", "--port=8001"), (Path("."), False, 8001), {"default_file": None}),
        ((BASEPATH, "--no-view"), (Path(BASEPATH), False, 8000), {"default_file": None}),
        ((BASEPATH, "--port=8001"), (Path(BASEPATH), True, 8001), {"default_file": None}),
        ((BASEPATH, "--no-view", "--port=8001"), (Path(BASEPATH), False, 8001), {"default_file": None}),
        ((BASEPATH, "--port=8001"), (Path(BASEPATH), True, 8001), {"default_file": None}),
        (("--no-view", "--default-file=index.html"), (Path("."), False, 8000), {"default_file": Path("index.html")}),
        ((BASEPATH, "--default-file=index.html"), (Path(BASEPATH), True, 8000), {"default_file": Path("index.html")}),
        (("--port=8001", "--default-file=index.html"), (Path("."), True, 8001), {"default_file": Path("index.html")}),
        (("--no-view", "--port=8001", "--default-file=index.html"), (Path("."), False, 8001), {"default_file": Path("index.html")}),
        ((BASEPATH, "--no-view", "--default-file=index.html"), (Path(BASEPATH), False, 8000), {"default_file": Path("index.html")}),
        ((BASEPATH, "--port=8001", "--default-file=index.html"), (Path(BASEPATH), True, 8001), {"default_file": Path("index.html")}),
        ((BASEPATH, "--no-view", "--port=8001", "--default-file=index.html"), (Path(BASEPATH), False, 8001), {"default_file": Path("index.html")}),
        ((BASEPATH, "--port=8001", "--default-file=index.html"), (Path(BASEPATH), True, 8001), {"default_file": Path("index.html")}),
    ],
)
@mock.patch("pyscript.plugins.run.start_server")
def test_run_server_with_valid_combinations(
    start_server_mock, invoke_cli: CLIInvoker, run_args, expected_posargs, expected_kwargs  # noqa: F811
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
    start_server_mock.assert_called_once_with(*expected_posargs, **expected_kwargs)


class TestFolderBasedHTTPRequestHandler:
    def setup_method(self, method):
        # Create a test server instance with the custom handler
        CustomHTTPRequestHandler = get_folder_based_http_request_handler(Path("."))
        self.server = http.server.HTTPServer(("127.0.0.1", 0), CustomHTTPRequestHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

        # Get the port the server is listening on
        self.server_address = self.server.socket.getsockname()

    def teardown_method(self, method):
        # Clean up the server
        self.server.shutdown()
        self.server_thread.join()

    def test_headers(self):
        # Given a request to the test server
        connection = http.client.HTTPConnection(*self.server_address)
        connection.request("GET", "/")
        response = connection.getresponse()

        # Expect the custom headers to be present in the response
        assert response.getheader("Cross-Origin-Opener-Policy") == "same-origin"
        assert response.getheader("Cross-Origin-Embedder-Policy") == "require-corp"
        assert response.getheader("Cross-Origin-Resource-Policy") == "cross-origin"
