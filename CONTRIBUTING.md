# Contribution guide for developers

## Development

### Setting up the environment

To get started, you will need to setup the development environment. This goes
through two main steps, namely [(1) Installing `pyscript-cli` dependencies](#install-pyscript-cli-dependencies)
and [(2) Installing `pyscript-cli` Dev dependencies](#install-the-development-dependencies).

### Install `pyscript-cli` dependencies

`pyscript-cli` requires [`poetry`](https://python-poetry.org/) to manage dependencies
and setup the environment.

Therefore, the first thing to do is to make sure that you have `poetry` installed
in your current Python environment. Please refer to the official `poetry`
[documentation](https://python-poetry.org/docs/master/#installation) for installation
instructions.

To install `pyscript-cli` dependencies, you will need to run the following command from the project root:

```shell
poetry install
```

### Install the development dependencies

There are a few extra dependencies that are solely required for development.
To install these packages, you will need to run the following command from the project root:

```shell
poetry install --with dev-dependencies
```

Once all the dependencies are installed, you will only need to setup the git hooks
via [`pre-commit`](https://pre-commit.com/):

```shell
pre-commit install
```

## Documentation

### Install the documentation dependencies

To get started, you will need to install the documentation dependencies from the project root:

```shell
poetry install --extras docs
```

### The quickest way to get started

The following command (run from project root) will launch a live-reloaded session of the
documentation in your browser, effectively combining the steps detailed in the following sections:

```shell
poetry run make -C docs live
```

### Activate the environment

You will need to activate the virtual environment in order to use the dependencies that were
just installed:

```shell
poetry shell
```

Your prompt should now have a prefix, e.g.:

```shell
(pyscript-cli-_y5OiBT8-py3.9) mattkram [~/dev/pyscript-cli] $
```

### Generate the docs in live mode

The live mode will allow you to generate the documentation with live reload.

From the project root, run the following command :

```shell
make -C docs live
```

Or, alternately, navigate to the `docs` directory and run:

```shell
make live
```


Either of the above commands should launch a live dev server and you will be able to view the
docs in your browser.
As the files are updated, the docs should be refreshed.

### Generate static docs

If you don't want to use the live reload mode, simply replace either command above with `html`,
e.g.:

```shell
make -C docs html
```
