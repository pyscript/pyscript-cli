"""The main CLI entrypoint and commands."""
import sys
from typing import Any, Optional

from pluggy import PluginManager

from pyscript import __version__, app, console, plugins, typer
from pyscript.plugins import hookspecs

DEFAULT_PLUGINS = ["create", "wrap"]


def ok(msg: str = ""):
    """
    Simply prints "OK" and an optional message, to the console, before cleanly
    exiting.

    Provides a standard way to end/confirm a successful command.
    """
    console.print(f"OK. {msg}".rstrip(), style="green")
    raise typer.Exit()


class Abort(typer.Abort):
    """
    Abort with a consistent error message.
    """

    def __init__(self, msg: str, *args: Any, **kwargs: Any):
        console.print(msg, style="red")
        super().__init__(*args, **kwargs)


class Warning(typer.Exit):
    def __init__(self, msg: str, *args: Any, **kwargs: Any):
        console.print(msg, style="yellow")
        super().__init__(*args, **kwargs)


@app.callback(invoke_without_command=True, no_args_is_help=True)
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", help="Show project version and exit."
    )
):
    """
    Command Line Interface for PyScript.
    """
    if version:
        console.print(f"PyScript CLI version: {__version__}", style="bold green")
        raise typer.Exit()


pm = PluginManager("pyscript")

# @app.command()
# def wrap(
#     input_file: Optional[Path] = _input_file_argument,
#     output: Optional[Path] = _output_file_option,
#     command: Optional[str] = _command_option,
#     show: Optional[bool] = _show_option,
#     title: Optional[str] = _title_option,
# ) -> None:
#     """Wrap a Python script inside an HTML file."""
#     title = title or "PyScript App"
#
#     if not input_file and not command:
#         raise Abort(
#             "Must provide either an input '.py' file or a command with the '-c' option."
#         )
#     if input_file and command:
#         raise Abort("Cannot provide both an input '.py' file and '-c' option.")
#
#     # Derive the output path if it is not provided
#     remove_output = False
#     if output is None:
#         if command and show:
#             output = Path("pyscript_tmp.html")
#             remove_output = True
#         elif not command:
#             assert input_file is not None
#             output = input_file.with_suffix(".html")
#         else:
#             raise Abort("Must provide an output file or use `--show` option")
#
#     if input_file is not None:
#         parsing_res = file_to_html(input_file, title, output)
#         if parsing_res is not None:
#             msg_template = "WARNING: The input file contains some imports which are not currently supported PyScript.\nTherefore the code might not work, or require some changes.{packages}{locals}"
#             msg = msg_template.format(
#                 packages=f"\n{str(parsing_res.unsupported_packages)}"
#                 if parsing_res.unsupported_packages
#                 else "",
#                 locals=f"\n{str(parsing_res.unsupported_paths)}"
#                 if parsing_res.unsupported_paths
#                 else "",
#             )
#             raise Warning(msg=msg)
#
#     if command:
#         string_to_html(command, title, output)
#
#     assert output is not None
#
#     if show:
#         console.print("Opening in web browser!")
#         webbrowser.open(f"file://{output.resolve()}")
#
#     if remove_output:
#         time.sleep(1)
#         output.unlink()

pm.add_hookspecs(hookspecs)
for modname in DEFAULT_PLUGINS:
    importspec = f"pyscript.plugins.{modname}"
    try:
        __import__(importspec)
    except ImportError as e:
        raise ImportError(
            f'Error importing plugin "{modname}": {e.args[0]}'
        ).with_traceback(e.__traceback__) from e
    else:
        mod = sys.modules[importspec]
        pm.register(mod, modname)
    loaded = pm.load_setuptools_entrypoints("pyscript")

for cmd in pm.hook.pyscript_subcommand():
    plugins._add_cmd(cmd)
