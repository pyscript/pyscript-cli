import os
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

        httpd.serve_forever()


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
    except KeyboardInterrupt:
        print("\nStopping server... Bye bye!")
        raise typer.Exit()
    except OSError as e:
        if e.errno == 48:
            console.print(
                f"Error: Port {port} is already in use!",
                style="red",
            )
            kill_current_process = typer.prompt(
                "Do you want to kill the current process and run this app instead?"
            )
            breakpoint()
            if kill_current_process == "y":
                # Kill the current process serving on the port.
                os.system(f"lsof -ti:{port} | xargs kill -9")
            else:
                console.print("Aborting... Choose another port and try again.")
                raise typer.Exit()

        console.print(f"Error: {e.strerror}", style="red")
        raise typer.Exit()


@plugins.register
def pyscript_subcommand():
    return run
