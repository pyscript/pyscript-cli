# User Guide

## Developing a new plugin

### Making your plugin discoverable

To register a python module/package as a new a `pyscript` CLI plugin, it's first
necessary to register that plugin via `setuptools.entrypoints`. To do so, if you
are using a `setup.py` file, you'll need to add the following to it:

```
entry_points={"pyscript-cli": ["<plugin-name> = <plugin-module>"]}
```

otherwise, if you are using `Poetry`, you'll need to add the following to your
`pyproject.toml` file:

```
[tool.poetry.plugins."pyscript-cli"]
<plugin-name> = "<plugin-module>"
```

### Extending `pyscript` CLI with new commands

To create new commands in your plugin and make them available in the `pyscript`
CLI, create a function and then register it like below.

```python
from pyscript import console, plugins


def create():
    """Creates a new PyScript Project from scratch."""
    console.print("pyscript create cmd not yet available..", style="bold green")
    return True


@plugins.register
def pyscript_subcommand():
    return create
```
