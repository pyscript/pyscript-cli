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

```shell
$ pip install pyscript
```

## Usage

### Embed a Python script into a PyScript HTML file

```shell
$ pyscript wrap <filename.py>
```

This will generate a file called `<filename.html>` by default.
This can be overwritten with the `-o` or `--output` option:

```shell
$ pyscript wrap <filename.py> -o <another_filename.html>
```

### Open the script inside the browser using the `--show` option

```shell
$ pyscript wrap <filename.py> --show
```

### Set a title for the browser tab

You can set the title of the browser tab with the `--title` option:

```shell
$ pyscript wrap <filename.py> --title "My cool app!"
```

### Very simple command examples with `--command` option

The `-c` or `--command` option can be used to demo very simple cases.
In this case, if the `--show` option is used and no `--output` file is used, a temporary file will be generated.

```shell
$ pyscript wrap -c 'print("Hello World!")' --show
```
