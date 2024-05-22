import json
import os
import re
import tarfile
import tempfile
from pathlib import Path
from typing import Optional

import requests
import toml
import typer

from pyscript import app, cli, plugins
from pyscript._generator import (
    _get_latest_pyscript_version,
    _get_latest_repo_version,
    save_config_file,
)


@app.command()
def convert_offline(
    path: str = typer.Argument(
        None, help="Path to pyscript project to convert for offline usage"
    ),
    config_files: str = typer.Option(
        "pyscript.toml", "--config-files", help="Comma-separated list of config files"
    ),
    interpreter: str = typer.Option(
        "pyodide",
        "--interpreter",
        help="Choose which interpreter to configure. Choices are 'pyodide' or 'micropython'",
    ),
    download_full_pyodide: bool = typer.Option(
        False,
        "--download-full-pyodide",
        help="Download the 200MB+ pyodide libraries instead of just required interpreter",
    ),
):
    """
    Takes an existing pyscript app and converts it for offline usage
    """
    app_path = Path(path)
    PYSCRIPT_TAR_URL_BASE = (
        "https://pyscript.net/releases/{pyscript_version}/release.tar"
    )
    PYODIDE_TAR_URL_BASE = "https://github.com/pyodide/pyodide/releases/download/{pyodide_version}/{pyodide_tar_name}-{pyodide_version}.tar.bz2"
    MPY_BASE_URL = (
        "https://cdn.jsdelivr.net/npm/@micropython/micropython-webassembly-pyscript/"
    )
    remote_pyscript_pattern = re.compile(r"https://pyscript.net/releases/[\d.]+/")

    if interpreter not in ("pyodide", "micropython"):
        raise cli.Abort("Interpreter must be one of 'pyodide' or 'micropython'")

    # Get first app configuration to pull pyscript version
    config_files_list = config_files.split(",")
    config_path = app_path / config_files_list[0]
    config = _get_config(config_path)

    # Get the required pyscript version based on config
    pyscript_version = config.get("version", "latest")
    if pyscript_version == "latest":
        pyscript_version = _get_latest_pyscript_version()

    pyscript_tar_url = PYSCRIPT_TAR_URL_BASE.format(pyscript_version=pyscript_version)
    pyscript_files_dir = app_path / "pyscript"

    # Download and extract pyscript files
    print("Downloading pyscript files...")
    _download_and_extract_tarfile(pyscript_tar_url, pyscript_files_dir)
    print("Downloading and extraction of pyscript files successful.")

    # Download and extract pyodide files
    print("Downloading pyodide files...")
    pyodide_version = _get_latest_repo_version("pyodide", "pyodide", "")
    if not pyodide_version:
        raise cli.Abort("Unable to retrieve latest pyodide version from Github")

    # Only download the 200MB+ pyodide libraries if required, else just download
    # the core
    pyodide_tar_name = "pyodide" if download_full_pyodide else "pyodide-core"
    pyodide_tar_url = PYODIDE_TAR_URL_BASE.format(
        pyodide_version=pyodide_version, pyodide_tar_name=pyodide_tar_name
    )
    _download_and_extract_tarfile(pyodide_tar_url, app_path)
    print("Downloading and extraction of pyodide files successful.")

    # Download Micropython files
    print("Downloading micropython files...")
    mpy_path = app_path / "micropython"
    mpy_path.mkdir(exist_ok=True)
    files = ("micropython.mjs", "micropython.wasm")

    for file in files:
        target_path = mpy_path / file
        url = MPY_BASE_URL + file

        # wasm file is bytes format, mjs is text
        response = requests.get(url)
        if "wasm" in file:
            with open(target_path, "wb") as fp:
                fp.write(response.content)
        else:
            with open(target_path, "w") as fp:
                fp.write(response.text)
    print("Downloading of micropython files sucessful")

    # Finding all HTML files
    html_files = []
    for dirname, dirs, filenames in os.walk(app_path):
        dirpath = Path(dirname)
        html_files.extend([dirpath / f for f in filenames if f.endswith(".html")])

    # Replace remote resources with freshly downloaded resources
    # Also for old config format to warn user
    old_config_pattern = re.compile(r"py-config>")
    found_old_config = False

    for filepath in html_files:
        with open(filepath) as fpi:
            content = fpi.read()

        if remote_pyscript_pattern.search(content):
            new_content = remote_pyscript_pattern.sub("/pyscript/", content)
            with open(filepath, "w") as fpo:
                fpo.write(new_content)
                print(f"Updated {filepath}")

        found_old_config = found_old_config or bool(old_config_pattern.search(content))

    # Add/replace interpreter with downloaded interpreter
    for config_file in config_files_list:
        config_file_path = app_path / config_file
        config = _get_config(config_file_path)
        config["interpreter"] = f"/{interpreter}/{interpreter}.mjs"
        save_config_file(config_file_path, config)

        print(f"Updated {config_file_path}")

    if found_old_config:
        print(
            "WARNING: <py-config> and <mpy-config> are not currently supported by this tool"
        )


def _download_and_extract_tarfile(remote_url: str, extract_dir: Path):
    """Downloads the tarfile at `remote_url` and extracts it into `extract_dir`

    Params:
        - remote_url(str): URL of the tarball, for example https://example.com/file.tar
        - extract_dir(Path): directory to extract the tarball into
    """
    with tempfile.TemporaryDirectory() as tempdirname:
        tarfile_target = Path(tempdirname) / "temp.tar"
        response = requests.get(remote_url, stream=True)
        if response.status_code == 200:
            with open(tarfile_target, "wb") as fp:
                fp.write(response.raw.read())
        else:
            raise cli.Abort(
                f"Unable to download required files. Please check your network connection"
            )

        with tarfile.open(tarfile_target, "r") as tfile:
            tfile.extractall(path=extract_dir)


def _get_config(config_path: Path):
    """Loads the configuration from the given Path"""
    if "toml" in str(config_path):
        return toml.load(config_path)
    elif "json" in str(config_path):
        with open(config_path) as fp:
            return json.load(fp)
