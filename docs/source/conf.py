"""Documentation configuration for `pyscript-cli`."""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import toml

# Ensure the package is in the path
project_root = Path(__file__).parents[2]
sys.path.insert(0, (project_root / "src").as_posix())

# General information about the project.
project = "pyscript-cli"
author = "Anaconda"
copyright = f"2022 - {datetime.now().year}, {author}"

# Load the package version from pyproject.toml
with (project_root / "pyproject.toml").open("r") as fp:
    version = toml.load(fp)["tool"]["poetry"]["version"]
    release = version


# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]
exclude_patterns: list[str] = []

# The suffix(es) of source filenames.
source_suffix = [".rst", ".md"]

# The master toctree document.
master_doc = "index"

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

autodoc_default_options = {
    "members": None,
    "undoc-members": None,
    "show-inheritance": None,
}

# The theme to use for HTML and HTML Help pages.
html_theme = "pydata_sphinx_theme"
# html_logo = "_static/avatar.jpeg"
html_favicon = "_static/avatar.jpeg"
html_theme_options = {
    "github_url": "https://github.com/pyscript/pyscript-cli",
    "icon_links": [
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/pyscript-cli",
            "icon": "fas fa-box",
        },
    ],
}
html_static_path = ["_static"]
