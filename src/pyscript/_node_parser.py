"""
ast-based parser to gather modules/package dependencies of a Python module.
Code adapted from the find-imports project, currently in graveyard archive.
"""
import ast
from pathlib import Path
from collections import namedtuple
from threading import local

from ._supported_packages import PACKAGE_RENAMES, STANDARD_LIBRARY, PYODIDE_PACKAGES


class UnsupportedFileType(Exception):
    pass


Environment = namedtuple("Environment", ["packages", "paths"])

# https://stackoverflow.com/a/58847554
class ModuleFinder(ast.NodeVisitor):
    def __init__(self, *args, **kwargs):
        self.packages = set()
        self.other_modules = set()
        super().__init__(*args, **kwargs)

    def visit_Import(self, node):
        for name in node.names:
            imported = name.name.split(".")[0]
            self._import_name(imported)

    def visit_ImportFrom(self, node):
        # if node.module is missing it's a "from . import ..." statement
        # if level > 0 it's a "from .submodule import ..." statement
        if node.module is not None and node.level == 0:
            imported = node.module.split(".")[0]
            self._import_name(imported)

    def _import_name(self, imported):
        pkg_name = PACKAGE_RENAMES.get(imported, imported)
        if pkg_name not in STANDARD_LIBRARY:
            if pkg_name in PYODIDE_PACKAGES:
                self.packages.add(pkg_name)
            else:
                self.other_modules.add(pkg_name)


def _find_modules(source: str, source_fpath: Path) -> Environment:
    fname = source_fpath.name
    # passing mode='exec' just in case defaults will change in the future
    nodes = ast.parse(source, fname, mode="exec")

    finder = ModuleFinder()
    finder.visit(nodes)
    print("Found modules: ", finder.packages, finder.other_modules)
    source_basefolder = source_fpath.parent
    local_mods = set(
        map(
            lambda p: Path(*p.parts[1:]),
            filter(
                lambda d: d.stem in finder.other_modules
                and ((d.is_file() and d.suffix == ".py") or d.is_dir()),
                source_basefolder.iterdir(),
            ),
        )
    )
    print("local modules", local_mods)
    print("external mods", finder.packages)
    return Environment(packages=finder.packages, paths=local_mods)


def _convert_notebook(source_fpath: Path) -> str:
    from nbconvert import ScriptExporter

    exporter = ScriptExporter()
    source, _ = exporter.from_filename(source_fpath)

    return source


def find_imports(source_fpath: Path) -> Environment:
    """
    Parse the input source, and returns its dependencies, as organised in 
    the sets of external packages, and local modules, respectively.
    Any modules or package with the same name found in the local

    Parameters
    ----------
    source_fpath : Path
        Path to the input Python module to parse

    Returns
    -------
    tuple[set[str], set[str]]
        Pair of external modules, and local modules
    """
    fname, extension = source_fpath.name, source_fpath.suffix
    if extension == ".py":
        with open(source_fpath, "rt") as f:
            source = f.read()

    elif extension == ".ipynb":
        try:
            import nbconvert
        except ImportError as e:  # pragma no cover
            raise ImportError(
                "Please install nbconvert to serve Jupyter Notebooks."
            ) from e

        source = _convert_notebook(source_fpath)

    else:
        raise UnsupportedFileType(
            "{} is neither a script (.py) nor a notebook (.ipynb)".format(fname)
        )

    return _find_modules(source, source_fpath)
