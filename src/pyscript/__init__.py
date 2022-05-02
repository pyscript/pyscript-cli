"""A CLI for PyScript!"""

try:
    from importlib import metadata
except ImportError:  # pragma: no cover
    import importlib_metadata as metadata  # type: ignore

try:
    __version__ = metadata.version("pyscript-cli")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
