from typing import Optional

from pyscript import LATEST_PYSCRIPT_VERSION, app, cli, plugins
from pyscript._generator import create_project

try:
    import rich_click.typer as typer
except ImportError:  # pragma: no cover
    import typer  # type: ignore


@app.command()
def create(
    app_name: str = typer.Argument(..., help="The name of your new app."),
    app_description: str = typer.Option(..., prompt=True),
    author_name: str = typer.Option(..., prompt=True),
    author_email: str = typer.Option(..., prompt=True),
    pyscript_version: Optional[str] = typer.Option(
        LATEST_PYSCRIPT_VERSION,
        "--pyscript-version",
        help="If provided, defines what version of pyscript will be used to create the app",
    ),
):
    """
    Create a new pyscript project with the passed in name, creating a new
    directory in the current directory.
    Inspired by Sphinx guided setup.
    TODO: Agree on the metadata to be collected from the user.
    """
    try:
        create_project(
            app_name, app_description, author_name, author_email, pyscript_version
        )
    except FileExistsError:
        raise cli.Abort(
            f"A directory called {app_name} already exists in this location."
        )


@plugins.register
def pyscript_subcommand():
    return create
