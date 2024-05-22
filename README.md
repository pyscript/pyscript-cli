# PyScript CLI

A command-line interface for [PyScript](https://pyscript.net).


[![Version](https://img.shields.io/pypi/v/pyscript.svg)](https://pypi.org/project/pyscript/)
[![Test](https://github.com/pyscript/pyscript-cli/actions/workflows/test.yml/badge.svg)](https://github.com/pyscript/pyscript-cli/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/pyscript/pyscript-cli/branch/main/graph/badge.svg?token=dCxt9oBQPL)](https://codecov.io/gh/pyscript/pyscript-cli)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/pyscript/pyscript-cli/main.svg)](https://results.pre-commit.ci/latest/github/pyscript/pyscript-cli/main)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

Quickly wrap Python scripts into a HTML template, pre-configured with [PyScript](https://pyscript.net).

```bash
❯ pyscript

 Usage: pyscript [OPTIONS] COMMAND [ARGS]...

 Command Line Interface for PyScript.

╭─ Options ──────────────────────────────────────────────────────────────────────────────────────╮
│ --version          Show project version and exit.                                              │
│ --help             Show this message and exit.                                                 │
╰────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────────────╮
│ create  Create a new pyscript project with the passed in name, creating a new directory in the │
│         current directory. Alternatively, use `--wrap` so as to embed a python file instead.   │
│ run     Creates a local server to run the app on the path and port specified.                  │
╰────────────────────────────────────────────────────────────────────────────────────────────────╯

```

## Installation

### Using Pip

```shell
$ pip install pyscript
```

### Installing the developer setup from the a repository clone


[see the Developer setup section on CONTRIBUTING page](CONTRIBUTING.md)

## Usage

### run

#### Spin up a local server to run on the path and specified port

```shell
$ pyscript run <path_of_folder>
```

This will serve the folder `path_of_folder` at `localhost:8000` by default
and will open the URL in a browser window. Default is current directory if
`path_of_folder` is not supplied.

To use a different port, use `--port` option.

```shell
$ pyscript run <path_of_folder> --port 9000
```

To avoid opening a browser window, use `--no-view` option.

```shell
$ pyscript run <path_of_folder> --no-view
```

To serve a default file (e.g., `index.html`) instead of a 404 HTTP status when a nonexistent file is accessed, use `--default-file` option.

```shell
pyscript run <path_of_folder> --default-file <name of default file>
```

### create

#### Create a new pyscript project with the passed in name, creating a new directory

```shell
$ pyscript create <name_of_app>
```

This will create a new directory named `name_of_app` under the current directory.

The interactive prompts will further ask for information such as `description of the app`,
`name of the author`, `email of the author`, etc. These of course can be provided via
options such as `--author-name` etc. Use `pyscript create --help` for more information.

The following files will be created:

- `index.html`: start page for the project
- `pyscript.toml`: project metadata and config file
- `main.py`: a "Hello world" python starter module

#### Use --wrap to embed a python file OR a command string

- ##### Embed a Python script into a PyScript HTML file

```shell
$ pyscript create --wrap <filename.py>
```

This will generate a project i.e. a new directory named `filename` under the current directory.

Similar to the above, interactive prompts will further ask for metadata information.

The following files will be created:

- `index.html`: start page for the project
- `pyscript.toml`: project metadata and config file
- `main.py`: contains code of `filename.py`

This can be overridden with the `-o` or `--output` option:

```shell
$ pyscript create --wrap <filename.py> -o <another_filename.html>
```

i.e. the HTML file created in the above directory will now be named `another_filename.html`

- ##### Very simple command examples with `--command` option

The `-c` or `--command` option can be used to demo very simple cases.

By default, the name of the project folder created will be `pyscript-command-app` with the HTML file named `index.html`.

`-o/--output` option can be used with the `-c/--command` option to configure name of the project folder as well
as the name of the resulting HTML file.

```shell
$ pyscript create --wrap -c 'print("Hello World!")' -o <output_filename.html>
```

This will generate a project i.e. a new directory named `output_filename` under the current directory.

Similar to the above, interactive prompts will further ask for metadata information.

The following files will be created:

- `output_filename.html`: start page for the project
- `pyscript.toml`: project metadata and config file
- `main.py`: contains code of the command string passed via `-c/--command`
