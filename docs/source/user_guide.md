# User Guide

## Developing a new plugin

Create a function, and then register it like below.

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
