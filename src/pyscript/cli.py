"""The main CLI entrypoint and commands."""
import webbrowser
from pathlib import Path
from typing import Any, Optional

from pyscript._generator import file_to_html, string_to_html

try:
    import rich_click.typer as typer
except ImportError:
    import typer  # type: ignore
from rich.console import Console

from pyscript import __version__

console = Console()
app = typer.Typer(add_completion=False)


def _print_version():
    console.print(f"PyScript CLI version: {__version__}", style="bold green")


@app.callback(invoke_without_command=True, no_args_is_help=True)
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", help="Show project version and exit."
    )
):
    """Command Line Interface for PyScript."""
    if version:
        _print_version()
        raise typer.Exit()


@app.command()
def version() -> None:
    """Show project version and exit."""
    _print_version()


_input_file_argument = typer.Argument(
    None,
    help="An optional path to the input .py script. If not provided, must use '-c' flag.",
)
_output_file_option = typer.Option(
    None,
    "-o",
    "--output",
    help="Path to the resulting HTML output file. Defaults to input_file with suffix replaced.",
)
_command_option = typer.Option(
    None, "-c", "--command", help="If provided, embed a single command string."
)
_show_option = typer.Option(None, help="Open output file in web browser.")


class Abort(typer.Abort):
    def __init__(self, msg: str, *args: Any, **kwargs: Any):
        console.print(msg, style="red")
        super().__init__(*args, **kwargs)


@app.command()
def wrap(
    input_file: Optional[Path] = _input_file_argument,
    output: Optional[Path] = _output_file_option,
    command: Optional[str] = _command_option,
    show: Optional[bool] = _show_option,
) -> None:
    """Wrap a Python script inside an HTML file."""
    if input_file is not None:
        if command is not None:
            raise Abort("Cannot provide both an input file and `-c` option.")
        file_to_html(input_file, output)

    if command:
        if output is None:
            raise Abort("Must provide an output file or use `--show` option")
        string_to_html(command, output)

    if show:
        if output is None:
            raise Abort("Must provide an output file to use `--show` option")
        console.print("Opening in web browser!")
        webbrowser.open(f"file://{output.resolve()}")
