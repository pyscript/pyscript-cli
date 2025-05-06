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

Create a local environment with your environment manager of choice.

### Virtualenv

In case you choose Virtualenv, make a virtualenv and activate it using the following commands:

```shell
python -m venv .venv
source .venv/bin/activate
```

### Conda

In case you choose to use conda, use the following commands:

```shell
conda create -n pyscript-cli python=3.13
conda activate pyscript-cli
```

### Installation

Now that you have your environment set up and activated, install your local environment dependencies

```shell
pip install -e ".[dev]"
```

## Use the CLI

It is now possible to normally use the CLI. For more information on how to use it and it's commands, see the [Use the CLI section of the README](README.md)

## Run the tests

After setting up your developer environment, you can run the tests with the following command from the root directory:

```shell
pytest .
```

# Running CLI Commands

Once the installation process is done, the `pyscript` CLI is available to be used once the environment has been
activated. Simply run `pyscript` with the appropriate command. For instance, to see the list of commands:

```shell
>> pyscript --help

 Usage: pyscript [OPTIONS] COMMAND [ARGS]...

 Command Line Interface for PyScript.

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --version          Show project version and exit.                                                                                                                    │
│ --help             Show this message and exit.                                                                                                                       │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ create  Create a new pyscript project with the passed in name, creating a new directory in the current directory. Alternatively, use `--wrap` so as to embed a       │
│         python file instead.                                                                                                                                         │
│ run     Creates a local server to run the app on the path and port specified.                                                                                        │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

or, to run a pyscript app:

```shell
>> pyscript run
Serving from /pyscript-example at port 8000. To stop, press Ctrl+C.
127.0.0.1 - - [30/Apr/2025 17:01:03] "GET / HTTP/1.1" 200 -
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


## Creating a New Release

To create a new release of pyscript-cli, follow these steps:

1. Update the version number in `src/pyscript/version`

2. Update CHANGELOG.md with the changes since the last release

3. Create a new git tag matching the version number:
   ```shell
   git tag X.Y.Z
   ```

4. Push the tag to GitHub:
   ```shell
   git push origin X.Y.Z
   ```

5. The GitHub Actions workflow will automatically:
   - Verify the tag matches the version in `src/pyscript/version`
   - Run tests
   - Build and publish the package to PyPI
   - Create a GitHub release

6. Verify the new version is available on PyPI: https://pypi.org/project/pyscript-cli/

Note: Make sure all tests pass locally before creating a new release. The release workflow will fail if there are any test failures or version mismatches.

Note 2: The version number in `src/pyscript/version` and the tag pushed to git (`X.Y.Z` in the example above) MUST MATCH! If they don't match the, the
action to create and publish the release won't start.


### How the Release Process Works

The release process is automated through GitHub Actions workflows. Here's what happens behind the scenes:

1. When a new tag is pushed, it triggers the release workflow
2. The workflow first checks that:
   - The tag name matches the version in `src/pyscript/version`
   - All tests pass successfully

3. If checks pass, the workflow:
   - Builds the Python package using setuptools
   - Creates source and wheel distributions
   - Uploads the distributions to PyPI using twine
   - Creates a GitHub release with the tag name

4. The version check is performed by the `check_tag_version()` function in setup.py, which:
   - Reads the version from `src/pyscript/version`
   - Compares it to the git tag that triggered the workflow
   - Fails if they don't match exactly

5. The PyPI upload uses credentials stored as GitHub repository secrets

This automated process ensures consistent and reliable releases while preventing common issues like version mismatches or failed tests from being published.
