import socketserver
import webbrowser
from http.server import SimpleHTTPRequestHandler
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

    with socketserver.TCPServer(("", port), SimpleHTTPRequestHandler) as httpd:
        print(f"Serving at port {port}")
        webbrowser.open_new_tab(f"http://localhost:{port}/")
        httpd.serve_forever()

    if show:
        console.print("Opening in web browser!")


@plugins.register
def pyscript_subcommand():
    return run
