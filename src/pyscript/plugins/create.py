from pyscript import console, plugins


def create():
    """Creates a new PyScript Project from scratch."""
    console.print(f"pyscript create cmd not yet available..", style="bold green")
    return True

@plugins.register
def pyscript_subcommand():
    return create   
    