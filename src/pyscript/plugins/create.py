from typing import Optional

import typer

from pyscript import app, cli, plugins
from pyscript._generator import create_project


@app.command()
def create(
    app_or_file_name: Optional[str] = typer.Argument(
        None, help="The name of your new app or path to an input .py script"
    ),
    app_description: str = typer.Option(None, help="App description"),
    author_name: str = typer.Option(None, help="Name of the author"),
    author_email: str = typer.Option(None, help="Email of the author"),
    pyscript_version: str = typer.Option(
        None,
        "--pyscript-version",
        help="If provided, defines what version of pyscript will be used to create the app",
    ),
    project_type: str = typer.Option(
        "app",
        "--project-type",
        help="Type of project that is being created. Supported types are: 'app'",
    ),
    wrap: bool = typer.Option(
        False,
        "-w",
        "--wrap",
        help="Use wrap mode i.e. embed a python script into an HTML file",
    ),
    command: Optional[str] = typer.Option(
        None,
        "-c",
        "--command",
        help="If provided, embed a single command string. Meant to be used with `--wrap`",
    ),
    output: Optional[str] = typer.Option(
        None,
        "-o",
        "--output",
        help="""Name of the resulting HTML output file. Meant to be used with `-w/--wrap`""",
    ),
):
    """
    Create a new pyscript project with the passed in name, creating a new
    directory in the current directory. Alternatively, use `--wrap` so as to embed
    a python file instead.
    """
    if not app_or_file_name and not command:
        app_or_file_name = typer.prompt("App name", default="my-pyscript-app")

    if app_or_file_name and command:
        raise cli.Abort("Cannot provide both an input '.py' file and '-c' option.")

    if (output or command) and (not wrap):
        raise cli.Abort(
            """`--output/-o`, and `--command/-c`
            are meant to be used with `--wrap/-w`"""
        )

    if not app_description:
        app_description = typer.prompt("App description", default="")
    if not author_name:
        author_name = typer.prompt("Author name", default="")
    if not author_email:
        author_email = typer.prompt("Author email", default="")

    try:
        create_project(
            app_or_file_name,
            app_description,
            author_name,
            author_email,
            pyscript_version,
            project_type,
            wrap,
            command,
            output,
        )
    except FileExistsError:
        raise cli.Abort(
            f"A directory called {app_or_file_name} already exists in this location."
        )


@plugins.register
def pyscript_subcommand():
    return create
