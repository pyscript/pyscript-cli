from pyscript import app, console
from pyscript.plugins import add_cmd, hookimpl

# @app.command()
# def create():
#     """Creates a new PyScript Project from scratch."""
#     console.print(f"PyScript CLI MADE IT!", style="bold green")
#     return True


def create():
    console.print(f"PyScript CLI MADE IT!", style="bold green")
    return True


@hookimpl
def register_cmd():
    return create
