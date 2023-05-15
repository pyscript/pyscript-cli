import socketserver
import threading
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler
from typing import Optional

from pyscript import app, console, plugins

try:
    import rich_click.typer as typer
except ImportError:  # pragma: no cover
    import typer  # type: ignore


def start_server(path: str, show: bool, port: int):
    """
    Creates a local server to run the app on the path and port specified.
    """
    with socketserver.TCPServer(("", port), SimpleHTTPRequestHandler) as httpd:
        print(f"Serving at port {port}. To stop, press Ctrl+C.")
        if show:
            # Open the web browser in a separate thread after 0.5 seconds.
            open_browser = partial(webbrowser.open_new_tab, f"http://localhost:{port}/")
            threading.Timer(0.5, open_browser).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server... Bye bye!")

            # Clean after ourselves....
            httpd.shutdown()
            httpd.socket.close()
            raise typer.Exit()


@app.command()
def run(
    path: str = typer.Option(".", help="The path of the project that will run."),
    show: Optional[bool] = typer.Option(True, help="Open the app in web browser."),
    port: Optional[int] = typer.Option(8000, help="The port that the app will run on."),
):
    """
    Creates a local server to run the app on the path and port specified.
    """

    try:
        start_server(path, show, port)
    except OSError as e:
        if e.errno == 48:
            console.print(
                f"Error: Port {port} is already in use! :( Please, stop the process using that port"
                f"or ry another port using the --port option.",
                style="red",
            )
        else:
            console.print(f"Error: {e.strerror}", style="red")

        raise typer.Exit()


@plugins.register
def pyscript_subcommand():
    return run
