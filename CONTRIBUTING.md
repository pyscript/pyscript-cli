# Contribution guide for developers

## Developer setup

* Create a [fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo) of the [PyScript-CLI github repository](https://github.com/pyscript/pyscript-cli/fork) to your own GitHub account.

* [Clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) your newly forked version of the PyScript-CLI repository onto your local development machine. For example, use this command in your terminal:

    ```sh
    git clone https://github.com/<YOUR USERNAME>/pyscript-cli
    ```

    > **WARNING**: In the URL for the forked PyScript-CLI repository, remember to replace
        `<YOUR USERNAME>` with your actual GitHub username.

* Change into the root directory of your newly cloned `pyscript-cli` repository:

    ```sh
    cd pyscript-cli
    ```

* Add the original PyScript-CLI repository as your `upstream` to allow you to keep your own fork up-to-date with the latest changes:

    ```sh
    git remote add upstream https://github.com/pyscript/pyscript-cli.git
    ```

* If the above fails, try this alternative:

  ```sh
  git remote remove upstream
  ```

  ```sh
  git remote add upstream git@github.com:pyscript/pyscript-cli.git
  ```

* Pull in the latest changes from the main `upstream` PyScript repository:

    ```sh
    git pull upstream main
    ```

    > Contribute changes using the [GitHub flow model](https://docs.github.com/en/get-started/using-github/github-flow) of coding collaboration.

* (Recommended) Upgrade local pip:

    ```shell
    pip install --upgrade pip
    ```

* Make a virtualenv and activate it:

    ```shell
    python -m venv .venv
    source .venv/bin/activate
    ```

* Install your local enviroment dependencies

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
pip install -e ".[docs]"
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
