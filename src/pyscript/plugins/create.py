import time
import webbrowser
from pathlib import Path
from typing import Optional

import typer

from pyscript import LATEST_PYSCRIPT_VERSION, app, cli, console, plugins
from pyscript._generator import create_project, file_to_html, string_to_html


@app.command()
def create(
    app_or_file_name: Optional[Path] = typer.Argument(
        None, help="The name of your new app or path to an input .py script"
    ),
    app_description: str = typer.Option(None, help="App description"),
    author_name: str = typer.Option(None, help="Name of the author"),
    author_email: str = typer.Option(None, help="Email of the author"),
    pyscript_version: str = typer.Option(
        LATEST_PYSCRIPT_VERSION,
        "--pyscript-version",
        help="If provided, defines what version of pyscript will be used to create the app",
    ),
    project_type: str = typer.Option(
        "app",
        "--project-type",
        help="Type of project that is being created. Supported types are: 'app' or 'plugin'",
    ),
    wrap: Optional[bool] = typer.Option(
        False,
        "-w",
        "--wrap",
        help="Use wrap mode i.e. embed a python script into an HTML file",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "-o",
        "--output",
        help="""Path to the resulting HTML output file. Defaults to input_file with suffix replaced.
        Meant to be used with `--wrap`""",
    ),
    command: Optional[str] = typer.Option(
        None,
        "-c",
        "--command",
        help="If provided, embed a single command string. Meant to be used with `--wrap`",
    ),
    title: Optional[str] = typer.Option(
        None, help="Add title to HTML file. Meant to be used with `--wrap`"
    ),
    show: Optional[bool] = typer.Option(
        False,
        "--show",
        help="Open output file in web browser. Meant to be used with `--wrap`",
    ),
):
    """
    Create a new pyscript project with the passed in name, creating a new
    directory in the current directory. Alternatively, use `--wrap` so as to embed
    a python file instead.
    """
    if not app_or_file_name and not command:
        raise cli.Abort(
            "Must provide either an input '.py' file or a command with the '-c' option."
        )

    if app_or_file_name and command:
        raise cli.Abort("Cannot provide both an input '.py' file and '-c' option.")

    if (title or output or show or command) and (not wrap):
        raise cli.Abort(
            """`--title`, `--output/-o`, `--show` and `--command/-c`
            are meant to be used with `--wrap/-w`"""
        )

    if not wrap:
        try:
            if not app_description:
                app_description = typer.prompt("App description")
            if not author_name:
                author_name = typer.prompt("Author name")
            if not author_email:
                author_email = typer.prompt("Author email")
            create_project(
                app_or_file_name,
                app_description,
                author_name,
                author_email,
                pyscript_version,
                project_type,
            )
        except FileExistsError:
            raise cli.Abort(
                f"A directory called {app_or_file_name} already exists in this location."
            )
    else:
        title = title or "PyScript App"

        # Derive the output path if it is not provided
        remove_output = False
        if output is None:
            if command and show:
                output = Path("pyscript_tmp.html")
                remove_output = True
            elif not command:
                assert app_or_file_name is not None
                output = app_or_file_name.with_suffix(".html")
            else:
                raise cli.Abort("Must provide an output file or use `--show` option")
        if app_or_file_name is not None:
            file_to_html(
                app_or_file_name,
                title,
                output,
                template_name="wrap.html",
                pyscript_version=pyscript_version,
            )
        if command:
            string_to_html(
                command,
                title,
                output,
                template_name="wrap.html",
                pyscript_version=pyscript_version,
            )
        if output:
            if show:
                console.print("Opening in web browser!")
                webbrowser.open(f"file://{output.resolve()}")
            if remove_output:
                time.sleep(1)
                output.unlink()


@plugins.register
def pyscript_subcommand():
    return create
