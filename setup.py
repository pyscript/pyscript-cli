import os
from setuptools import setup

def read_version():
    with open("src/pyscript/version", "r") as f:
        return f.read().strip("\n")

def check_tag_version():
    tag = os.getenv("GITHUB_REF")
    expected_version = read_version()
    if tag != f"refs/tags/{expected_version}":
        raise Exception(f"Tag '{tag}' does not match the expected "
                        f"version '{expected_version}'")

with open("README.md", "r") as fh:
    long_description = fh.read()

check_tag_version()

setup(
    name="pyscript",
    version=read_version(),
    description="Command Line Interface for PyScript",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pyscript/pyscript-cli",
    author="Matt Kramer, Fabio Pliger, Nicholas Tollervey, Fabio Rosado, Madhur Tandon",
    author_email="mkramer@anaconda.com, fpliger@anaconda.com, ntollervey@anaconda.com, frosado@anaconda.com, mtandon@anaconda.com",
    license="Apache-2.0",
    install_requires=[
        'importlib-metadata; python_version<"3.8"',
        'Jinja2<3.2',
        'pluggy<1.3',
        'rich<=13.7.1',
        'toml<0.11',
        'typer<=0.9.0',
        'platformdirs<4.3',
        'requests<=2.31.0',
    ],
    python_requires=">=3.9",
    keywords=["pyscript", "cli", "pyodide", "micropython", "pyscript-cli"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Pre-processors',
    ],
    extras_require={
        "dev": [
            "coverage<7.3",
            "mypy<=1.4.1",
            "pytest<7.5",
            "types-toml<0.11",
            "types-requests"
        ],
        "docs": [
            "Sphinx<5.2",
            "sphinx-autobuild<2021.4.0",
            "sphinx-autodoc-typehints<1.20",
            "myst-parser<0.19.3",
            "pydata-sphinx-theme<0.13.4"
        ]
    },
    entry_points={
        'console_scripts': [
            'pyscript = pyscript.cli:app',
        ],
    },
    project_urls={
        'Documentation': 'https://docs.pyscript.net',
        'Examples': 'https://pyscript.com/@examples',
        'Homepage': 'https://pyscript.net',
        'Repository': 'https://github.com/pyscript/pyscript-cli',
    },
)
