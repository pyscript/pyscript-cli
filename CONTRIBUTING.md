# Contribution guide for developers

## Developer setup

Git clone the repository:

```shell
git clone https://github.com/pyscript/pyscript.git
```

(Recommended) Upgrade local pip:

```shell
pip install --upgrade pip
```

Make a virtualenv and activate it:

```shell
python -m venv .venv
. .venv/bin/activate
```

Install your local enviroment dependencies

```shell
pip install -e ".[dev]"
```

## Use the CLI

It is now possible to normally use the CLI. For more information on how to use it and it's commands, see the [Use the CLI section of the README](README.md)

## Run the tests

After setting up your developer enviroment, you can run the tests with the following command from the root directory:

```shell
pytest .
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
