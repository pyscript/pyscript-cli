"""
ast-based parser to gather modules/package dependencies of a Python module.
Code adapted from the find-imports project, currently in graveyard archive.
"""
import ast
from inspect import Attribute
import os
import pkgutil
from pathlib import Path
from typing import Union
from collections import namedtuple, defaultdict
from itertools import filterfalse, chain

from ._supported_packages import PACKAGE_RENAMES, STANDARD_LIBRARY, PYODIDE_PACKAGES


class UnsupportedFileType(Exception):
    pass


ImportInfo = namedtuple("ImportInfo", ["packages", "paths"])


class NamespaceInfo:
    def __init__(self, source_fpath: Path) -> None:
        # expanding base_folder to absolute as pkgutils.FileFinder will do so - easier for later purging
        self.base_folder = str(source_fpath.parent.absolute())
        self.source_mod_name = source_fpath.stem
        self._collect()
        # storing this as it will be useful for multiple lookups
        self._all_namespace = set(chain(self.modules, self.packages))

    def _collect(self):
        iter_modules_paths = [self.base_folder]
        for root, dirs, files in os.walk(self.base_folder):
            for dirname in dirs:
                iter_modules_paths.append(os.path.join(root, dirname))

        # need to consume generator as I will iterate two times for packages, and modules
        pkg_mods = tuple(pkgutil.iter_modules(iter_modules_paths))
        modules = map(
            lambda mi: os.path.join(mi.module_finder.path, mi.name),
            filterfalse(
                lambda mi: mi.ispkg or mi.name == self.source_mod_name, pkg_mods
            ),
        )
        packages = map(
            lambda mi: os.path.join(mi.module_finder.path, mi.name),
            filter(lambda mi: mi.ispkg, pkg_mods),
        )
        self.modules = set(map(self._dotted_path, modules))
        self.packages = set(map(self._dotted_path, packages))

    def _dotted_path(self, p: str):
        p = p.replace(self.base_folder, "").replace(os.path.sep, ".")
        if p.startswith("."):
            p = p[1:]
        return p

    def __contains__(self, item: str) -> bool:
        return item in self._all_namespace

    def __str__(self) -> str:
        return f"NameSpace info for {self.base_folder} \n\t Modules: {self.modules} \n\t Packages: {self.packages}"

    def __repr__(self) -> str:
        return str(self)


class FinderResult:
    def __init__(self) -> None:
        self.packages = set()
        self.locals = set()
        self.unsupported = defaultdict(set)

    def add_package(self, pkg_name: str) -> None:
        self.packages.add(pkg_name)

    def add_locals(self, pkg_name: str) -> None:
        self.locals.add(pkg_name)

    def add_unsupported_external_package(self, pkg_name: str) -> None:
        self.unsupported["external"].add(pkg_name)

    def add_unsupported_local_package(self, pkg_name: str) -> None:
        self.unsupported["local"].add(pkg_name)

    @property
    def has_warnings(self):
        return len(self.unsupported) > 0

    @property
    def unsupported_packages(self):
        return self.unsupported["external"]

    @property
    def unsupported_paths(self):
        return self.unsupported["local"]


# https://stackoverflow.com/a/58847554
class ModuleFinder(ast.NodeVisitor):
    def __init__(self, context: NamespaceInfo, *args, **kwargs):
        # list of all potential local imports
        self.context = context
        self.results = FinderResult()
        super().__init__(*args, **kwargs)

    def visit_Import(self, node):
        for name in node.names:
            # need to check for absolute module import here as they won't work in PyScript
            # absolute package imports will be found later in _import_name
            if len(name.name.split(".")) > 1 and name.name in self.context:
                self.results.add_unsupported_local_package(name.name)
            else:
                self._import_name(name.name)

    def visit_ImportFrom(self, node):
        # if node.module is missing it's a "from . import ..." statement
        # if level > 0 it's a "from .submodule import ..." statement
        if node.module is not None:
            self._import_name(node.module)

    def _import_name(self, imported):
        if imported in self.context:
            if imported not in self.context.packages:
                self.results.add_locals(imported)
            else:
                self.results.add_unsupported_local_package(imported)
        else:
            imported = imported.split(".")[0]
            pkg_name = PACKAGE_RENAMES.get(imported, imported)
            if pkg_name not in STANDARD_LIBRARY:
                if pkg_name in PYODIDE_PACKAGES:
                    self.results.add_package(pkg_name)
                else:
                    self.results.add_unsupported_external_package(pkg_name)


def _find_modules(source: str, source_fpath: Path):
    fname = source_fpath.name
    # importing all local modules from source_fpath
    namespace_info = NamespaceInfo(source_fpath=source_fpath)
    # passing mode='exec' just in case defaults will change in the future
    nodes = ast.parse(source, fname, mode="exec")

    finder = ModuleFinder(context=namespace_info)
    finder.visit(nodes)
    report = finder.results
    pyenv_paths = map(
        lambda l: "{}.py".format(l.replace(".", os.path.sep)), report.locals
    )
    pyenv = ImportInfo(packages=report.packages, paths=set(pyenv_paths))
    if not report.has_warnings:
        return pyenv, None

    warnings = ImportInfo(
        packages=report.unsupported_packages, paths=report.unsupported_paths
    )
    return pyenv, warnings


def _convert_notebook(source_fpath: Path) -> str:
    from nbconvert import ScriptExporter

    exporter = ScriptExporter()
    source, _ = exporter.from_filename(source_fpath)

    return source


def find_imports(
    source_fpath: Path,
) -> Union[ImportInfo, tuple[ImportInfo, ImportInfo]]:
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
    Union[ImportInfo, tuple[ImportInfo, ImportInfo]]
        The function returns an instance of `ImportInfo` containing the 
        environment with packages and paths to include in py-env.
        Optionally, if the parsing detected unsupported packages and local modules, 
        this will be returned as well (still as `ImportInfo` instance)
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
