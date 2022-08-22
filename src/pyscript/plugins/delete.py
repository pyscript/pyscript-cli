from pyscript import app, console
from pyscript.plugins import add_cmd

@add_cmd
def delete():
    console.print(f"PyScript DELETED IT!", style="bold red")
    return True