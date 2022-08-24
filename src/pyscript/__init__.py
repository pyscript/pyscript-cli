"""A CLI for PyScript!"""

try:
    from importlib import metadata
except ImportError:  # pragma: no cover
    import importlib_metadata as metadata  # type: ignore

try:
    import rich_click.typer as typer
except ImportError:  # pragma: no cover
    import typer  # type: ignore
from rich.console import Console

try:
    __version__ = metadata.version("pyscript")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

console = Console()
app = typer.Typer(add_completion=False)
