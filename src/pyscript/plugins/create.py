from pyscript import app, console
from pyscript.plugins import add_cmd

# @app.command()
# def create():
#     """Creates a new PyScript Project from scratch."""
#     console.print(f"PyScript CLI MADE IT!", style="bold green")
#     return True
    
from pyscript.plugins import hookimpl


def create():
    console.print(f"PyScript CLI MADE IT!", style="bold green")
    return True

@hookimpl
def register_cmd():
    return create   
    