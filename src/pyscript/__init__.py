"""A CLI for PyScript!"""

import json
from pathlib import Path

import platformdirs
import typer
from rich.console import Console

LATEST_PYSCRIPT_VERSION = "2024.2.1"
APPNAME = "pyscript"
APPAUTHOR = "python"
DEFAULT_CONFIG_FILENAME = ".pyscriptconfig"

# Default initial data for the command line.
DEFAULT_CONFIG = {
    # Name of config file for PyScript projects.
    "project_config_filename": "pyscript.toml",
    "project_main_filename": "main.py",
}


DATA_DIR = Path(platformdirs.user_data_dir(appname=APPNAME, appauthor=APPAUTHOR))
CONFIG_FILE = DATA_DIR / Path(DEFAULT_CONFIG_FILENAME)
if not CONFIG_FILE.is_file():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w") as config_file:
        json.dump(DEFAULT_CONFIG, config_file)


try:
    from importlib import metadata
except ImportError:  # pragma: no cover
    import importlib_metadata as metadata  # type: ignore

try:
    __version__ = metadata.version("pyscript")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"


console = Console()
app = typer.Typer(add_completion=False)
with CONFIG_FILE.open() as config_file:
    config = json.load(config_file)

# Make sure all configuration keys are there. If any is missing,
# we pick from the default config
for k, v in DEFAULT_CONFIG.items():
    if k not in config:
        config[k] = v
