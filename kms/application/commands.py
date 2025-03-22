from cleo.commands.command import Command
from cleo.helpers import option
from kms.application.handlers import InitializeHandler


class Init(Command):
    name = "init"
    options = [
        option(
            "name",
            "N",
            """
             Specify the name of KeePass database when initializing.
            """,
        ),
        option(
            "database",
            "d",
            """Specify the path to the KeePass database when initializing, accessing or modifying the database.
            The config is ignored when this is given.""",
        ),
        option(
            "keyfile",
            "k",
            """Specify the path to the keyfile when initializing, accessing or modifying the database.
            No effect if --database is not given.
            """,
        ),
    ]
    handler: InitializeHandler

    def __init__(self, handler: InitializeHandler) -> None:
        super().__init__()
        self.handler = handler

    def handle(self):
        self.handler()


class Add(Command):
    arguments = []

    def handle(self): ...


class Show(Command):
    arguments = []

    def handle(self): ...


class Remove(Command):
    arguments = []

    def handle(self): ...


class Edit(Command):
    arguments = []

    def handle(self): ...


class Move(Command):
    arguments = []

    def handle(self): ...


class List(Command):
    arguments = []

    def handle(self): ...


class Grep(Command):
    arguments = []

    def handle(self): ...
