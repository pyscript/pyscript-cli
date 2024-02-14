"""The main CLI entrypoint and commands."""

import sys
from typing import Any, Optional

from pluggy import PluginManager

from pyscript import __version__, app, console, plugins, typer
from pyscript.plugins import hookspecs

DEFAULT_PLUGINS = ["create", "run"]


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


# Create the default PluginManager
pm = PluginManager("pyscript")

# Register the hooks specifications available for PyScript Plugins
pm.add_hookspecs(hookspecs)

# Register the default plugins available with the bare pyscript cli installation
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


# Load plugins registered via setuptools entrypoints
loaded = pm.load_setuptools_entrypoints("pyscript")

# Register the commands from plugins that have been loaded and used the
# `pyscript_subcommand` hook.
for cmd in pm.hook.pyscript_subcommand():
    plugins._add_cmd(cmd)
