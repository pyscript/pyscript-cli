# Changelog

All notable changes to the PyScript CLI will be documented in this file, with the latest release at the top.

## [0.3.0] - 2023-03-06

*A lot has changed between 0.2.5 and 0.3.6. This is a summary of the most important changes.*

### Features

- New command `run` to run a local server which serves the current directory.
  - Added the right CORS headers to the server running locally
  - Added no-cache headers to the server running locally to avoid caching issues while developing


## Improvements

- Allow users to specify an empty author name, email and app description when running `pyscript create`
- Merged `wrap` command into `create` command, so now `pyscript create` can create a new project or wrap an existing python file into a new pyscript project.
- The `pyscript create` command now prompts for a name if the name is not provided as an argument.
- You can now pass a single Python file to `pyscript create` and it will create a new project with the file's contents in the new `main.py` file - similar to using the `--wrap` option.

### Documentation

- Various improvements to the `README.md` files
- Added `CONTRIBUTING.md` file with information on how to contribute to the project and installing the development environment.
- Added `CHANGELOG.md` file to keep track of the changes in the project.
