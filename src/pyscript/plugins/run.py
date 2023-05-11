from typing import Optional

from pyscript import app, console, plugins

try:
    import rich_click.typer as typer
except ImportError:  # pragma: no cover
    import typer  # type: ignore


@app.command()
def run(
    path: str = typer.Option(".", help="The path of the project that will run."),
    show: Optional[bool] = typer.Option(True, help="Open the app in web browser."),
    port: Optional[int] = typer.Option(8000, help="The port that the app will run on."),
):
    """
    Creates a local server to run the app on the path and port specified.
    """

    if show:
        console.print("Opening in web browser!")


@plugins.register
def pyscript_subcommand():
    return run
