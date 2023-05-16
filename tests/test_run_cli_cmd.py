from __future__ import annotations

import pytest
from utils import CLIInvoker


@pytest.mark.parametrize(
    "path",
    ["non_existing_folder", "non_existing_file.html"],
    # ids=["passig", "command_and_script", "command_no_output_or_show"],
)
def test_run_bad_paths(invoke_cli: CLIInvoker, path: str):
    """
    Test that when wrap is called passing a bad path as input the command fails
    """
    # GIVEN a call to wrap with a bad path as argument
    result = invoke_cli("run", path)
    # EXPECT the command to fail
    assert result.exit_code == 1
    # EXPECT the right error message to be printed
    assert f"Error: Path {path} does not exist." in result.stdout
