"""The main CLI entrypoint and commands."""
import time
import webbrowser
from pathlib import Path
from typing import Any, Optional

from pyscript._generator import file_to_html, string_to_html


from pluggy import PluginManager

from pyscript import __version__, app, console, typer
from pyscript.plugins import create, delete, hookspecs, add_cmd


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
_title_option = typer.Option(None, help="Add title to HTML file.")


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
    title: Optional[str] = _title_option,
) -> None:
    """Wrap a Python script inside an HTML file."""
    title = title or "PyScript App"

    if not input_file and not command:
        raise Abort(
            "Must provide either an input '.py' file or a command with the '-c' option."
        )
    if input_file and command:
        raise Abort("Cannot provide both an input '.py' file and '-c' option.")

    # Derive the output path if it is not provided
    remove_output = False
    if output is None:
        if command and show:
            output = Path("pyscript_tmp.html")
            remove_output = True
        elif not command:
            assert input_file is not None
            output = input_file.with_suffix(".html")
        else:
            raise Abort("Must provide an output file or use `--show` option")

    if input_file is not None:
        file_to_html(input_file, title, output)

    if command:
        string_to_html(command, title, output)

    assert output is not None

    if show:
        console.print("Opening in web browser!")
        webbrowser.open(f"file://{output.resolve()}")

    if remove_output:
        time.sleep(1)
        output.unlink()

pm = PluginManager("pyscript-cli")

pm.add_hookspecs(hookspecs)

pm.load_setuptools_entrypoints("pyscript-cli")
pm.register(create)

for cmd in pm.hook.register_cmd():
    add_cmd(cmd)