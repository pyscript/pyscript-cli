"""A CLI for PyScript!"""
from pathlib import Path

import platformdirs
import toml

APPNAME = "pyscript"
APPAUTHOR = "python"

DATA_DIR = Path(platformdirs.user_data_dir(appname=APPNAME, appauthor=APPAUTHOR))
CONFIG_FILE = DATA_DIR / Path("pyscript.toml")

if not DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True)
    CONFIG_FILE.touch(exist_ok=True)

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
config = toml.load(CONFIG_FILE)
