from __future__ import annotations

import socketserver
import threading
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler
from pathlib import Path

import typer

from pyscript import app, cli, console, plugins


def get_folder_based_http_request_handler(
    folder: Path,
) -> type[SimpleHTTPRequestHandler]:
    """
    Returns a FolderBasedHTTPRequestHandler with the specified directory.

    Args:
        folder (str): The folder that will be served.

    Returns:
        FolderBasedHTTPRequestHandler: The SimpleHTTPRequestHandler with the
                                        specified directory.
    """

    class FolderBasedHTTPRequestHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=folder, **kwargs)

        def end_headers(self):
            self.send_header("Cross-Origin-Opener-Policy", "same-origin")
            self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
            self.send_header("Cross-Origin-Resource-Policy", "cross-origin")
            self.send_header("Cache-Control", "no-cache, must-revalidate")
            SimpleHTTPRequestHandler.end_headers(self)

    return FolderBasedHTTPRequestHandler


def split_path_and_filename(path: Path) -> tuple[Path, str]:
    """Receives a path to a pyscript project or file and returns the base
    path of the project and the filename that should be opened (filename defaults
    to "" (empty string) if the path points to a folder).

    Args:
        path (str): The path to the pyscript project or file.

    Returns:
        tuple(str, str): The base path of the project and the filename
    """
    abs_path = path.absolute()
    if path.is_file():
        return Path("/".join(abs_path.parts[:-1])), abs_path.parts[-1]
    else:
        return abs_path, ""


def start_server(path: Path, show: bool, port: int):
    """
    Creates a local server to run the app on the path and port specified.

    Args:
        path(str): The path of the project that will run.
        show(bool): Open the app in web browser.
        port(int): The port that the app will run on.

    Returns:
        None
    """
    # We need to set the allow_resuse_address to True because socketserver will
    # keep the port in use for a while after the server is stopped.
    # see https://stackoverflow.com/questions/31745040/
    socketserver.TCPServer.allow_reuse_address = True

    app_folder, filename = split_path_and_filename(path)
    CustomHTTPRequestHandler = get_folder_based_http_request_handler(app_folder)

    # Start the server within a context manager to make sure we clean up after
    with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
        console.print(
            f"Serving from {app_folder} at port {port}. To stop, press Ctrl+C.",
            style="green",
        )

        if show:
            # Open the web browser in a separate thread after 0.5 seconds.
            open_browser = partial(
                webbrowser.open_new_tab, f"http://localhost:{port}/{filename}"
            )
            threading.Timer(0.5, open_browser).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            console.print("\nStopping server... Bye bye!")

            # Clean up resources....
            httpd.shutdown()
            httpd.socket.close()
            raise typer.Exit(1)


@app.command()
def run(
    path: Path = typer.Argument(
        Path("."), help="The path of the project that will run."
    ),
    view: bool = typer.Option(True, help="Open the app in web browser."),
    port: int = typer.Option(8000, help="The port that the app will run on."),
):
    """
    Creates a local server to run the app on the path and port specified.
    """

    # First thing we need to do is to check if the path exists
    if not path.exists():
        raise cli.Abort(f"Error: Path {str(path)} does not exist.", style="red")

    try:
        start_server(path, view, port)
    except OSError as e:
        if e.errno == 48:
            console.print(
                f"Error: Port {port} is already in use! :( Please, stop the process using that port"
                f"or try another port using the --port option.",
                style="red",
            )
        else:
            console.print(f"Error: {e.strerror}", style="red")

        raise cli.Abort("")


@plugins.register
def pyscript_subcommand():
    return run
