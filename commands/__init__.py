# Commands for Split with Planes Add-in

from .contour import entry as splitWithPlanes

# List of commands to register
commands = [
    splitWithPlanes,
]


def start():
    """Called when add-in starts."""
    for command in commands:
        command.start()


def stop():
    """Called when add-in stops."""
    for command in commands:
        command.stop()
