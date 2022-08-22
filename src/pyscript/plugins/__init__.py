from pluggy import HookimplMarker
from pyscript import app

hookimpl = HookimplMarker("pyscript-cli")

def add_cmd(f):
    print(f"registering {f.__name__}")
    app.command()(f)


@hookimpl
def register_cmd(app, console):
    pass