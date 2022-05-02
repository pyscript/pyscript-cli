"""A CLI for PyScript!"""

from importlib import metadata

try:
    __version__ = metadata.version("pyscript-cli")
except metadata.PackageNotFoundError:
    __version__ = "unknown"
