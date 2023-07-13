# PyScript CLI

A command-line interface for [PyScript](https://pyscript.net).


[![Version](https://img.shields.io/pypi/v/pyscript.svg)](https://pypi.org/project/pyscript/)
[![Test](https://github.com/pyscript/pyscript-cli/actions/workflows/test.yml/badge.svg)](https://github.com/pyscript/pyscript-cli/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/pyscript/pyscript-cli/branch/main/graph/badge.svg?token=dCxt9oBQPL)](https://codecov.io/gh/pyscript/pyscript-cli)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/pyscript/pyscript-cli/main.svg)](https://results.pre-commit.ci/latest/github/pyscript/pyscript-cli/main)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

Quickly wrap Python scripts into a HTML template, pre-configured with [PyScript](https://pyscript.net).

<img src="https://user-images.githubusercontent.com/11037737/166966219-9440c3cc-e911-4730-882c-2ab9fa47147f.gif" style="width: 100%; max-width: 680px;" />

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

This will generate a file called `<filename.html>` by default.
This can be overwritten with the `-o` or `--output` option:

```shell
$ pyscript create --wrap <filename.py> -o <another_filename.html>
```

- ##### Open the script inside the browser using the `--show` option

```shell
$ pyscript create --wrap <filename.py> --show
```

- ##### Set a title for the browser tab

You can set the title of the browser tab with the `--title` option:

```shell
$ pyscript create --wrap <filename.py> --title "My cool app!"
```

- ##### Very simple command examples with `--command` option

The `-c` or `--command` option can be used to demo very simple cases.
In this case, if the `--show` option is used and no `--output` file is used, a temporary file will be generated.

```shell
$ pyscript create --wrap -c 'print("Hello World!")' --show
```
