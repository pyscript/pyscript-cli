from pluggy import HookspecMarker

hookspec = HookspecMarker("pyscript-cli")


@hookspec
def register_cmd():
    """My special little hook that you can customize."""
