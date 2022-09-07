"""
ast-based parser to gather modules/package dependencies of a Python module.
Code adapted from the find-imports project, currently in graveyard archive.
"""
from __future__ import annotations

import ast
import os
import pkgutil
from collections import defaultdict
from itertools import chain, filterfalse
from pathlib import Path

from ._supported_packages import PACKAGE_RENAMES, PYODIDE_PACKAGES, STANDARD_LIBRARY


class NamespaceInfo:
    def __init__(self, source_fpath: Path) -> None:
        # expanding base_folder to absolute as pkgutils.
        # FileFinder will do so - easier for later purging
        self.base_folder = str(source_fpath.parent.absolute())
        self.source_mod_name = source_fpath.stem
        self._collect()
        # storing this as it will be useful for multiple lookups
        self._all_namespace = set(chain(self.modules, self._packages))

    def _collect(self):
        iter_modules_paths = [self.base_folder]
        for root, dirs, files in os.walk(self.base_folder):
            for dirname in dirs:
                iter_modules_paths.append(os.path.join(root, dirname))

        # need to consume generator as I will iterate
        # two times for _packages, and modules
        pkg_mods = tuple(pkgutil.iter_modules(iter_modules_paths))
        modules = map(
            lambda mi: os.path.join(mi.module_finder.path, mi.name),
            filterfalse(
                lambda mi: mi.ispkg or mi.name == self.source_mod_name, pkg_mods
            ),
        )
        _packages = map(
            lambda mi: os.path.join(mi.module_finder.path, mi.name),
            filter(lambda mi: mi.ispkg, pkg_mods),
        )
        self.modules = set(map(self._dotted_path, modules))
        self._packages = set(map(self._dotted_path, _packages))

    def _dotted_path(self, p: str):
        p = p.replace(self.base_folder, "").replace(os.path.sep, ".")
        if p.startswith("."):
            p = p[1:]
        return p

    def __contains__(self, item: str) -> bool:
        return item in self._all_namespace

    def __str__(self) -> str:
        return (
            f"NameSpace info for {self.base_folder} \n\t "
            f"Modules: {self.modules} \n\t Packages: {self._packages}"
        )

    def __repr__(self) -> str:
        return str(self)


class FinderResult:
    def __init__(self) -> None:
        self._packages: set[str] = set()
        self._locals: set[str] = set()
        self._unsupported: defaultdict[str, set] = defaultdict(set)

    def add_package(self, pkg_name: str) -> None:
        self._packages.add(pkg_name)

    def add_locals(self, pkg_name: str) -> None:
        self._locals.add(pkg_name)

    def add_unsupported_external_package(self, pkg_name: str) -> None:
        self._unsupported["external"].add(pkg_name)

    def add_unsupported_local_package(self, pkg_name: str) -> None:
        self._unsupported["local"].add(pkg_name)

    @property
    def has_warnings(self):
        return len(self._unsupported) > 0

    @property
    def unsupported_packages(self):
        return self._unsupported["external"]

    @property
    def unsupported_paths(self):
        return self._unsupported["local"]

    @property
    def packages(self):
        return self._packages

    @property
    def paths(self):
        pyenv_paths = map(
            lambda l: "{}.py".format(l.replace(".", os.path.sep)), self._locals
        )
        return set(pyenv_paths)


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
            if imported not in self.context._packages:
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
    return finder.results


def _convert_notebook(source_fpath: Path) -> str:
    from nbconvert import ScriptExporter

    exporter = ScriptExporter()
    source, _ = exporter.from_filename(source_fpath)

    return source


def find_imports(
    source: str,
    source_fpath: Path,
) -> FinderResult:
    """
    Parse the input source, and returns its dependencies, as organised in
    the sets of external _packages, and local modules, respectively.
    Any modules or package with the same name found in the local

    Parameters
    ----------
    source  : str
        Python source code to parse
    source_fpath : Path
        Path to the input Python module to parse

    Returns
    -------
    FinderResult
        Return the results of parsing as a `FinderResult` instance.
        This instance provides reference to packages and paths to
        include in the py-env, as well as any unsupported import.
    """

    return _find_modules(source, source_fpath)
