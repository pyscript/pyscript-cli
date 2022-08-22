from pluggy import HookspecMarker

hookspec = HookspecMarker("pyscript-cli")


@hookspec
def pyscript_subcommand():
    """My special little hook that you can customize."""
