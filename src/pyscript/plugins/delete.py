from pyscript import console
from pyscript.plugins import register


def delete():
    console.print(f"pyscript delete cmd not yet available..", style="bold red")
    return True

@register
def pyscript_subcommand():
    return delete