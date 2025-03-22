import os
from functools import singledispatchmethod
from os.path import dirname
from typing import Any

from cleo.commands.command import Command
from cleo.helpers import option
from pykeepass import PyKeePass

from kms.application.configuration import KMSConfiguration
from kms.application.queries import (AbstractQuery, BooleanQuery, OptionQuery,
                                     ValueQuery)


class KmsCommand(Command):
    configuration = KMSConfiguration

    def __init__(self, configuration: KMSConfiguration) -> None:
        super().__init__()
        self.configuration = configuration

    @singledispatchmethod
    def prompt(self, query: AbstractQuery) -> Any:
        raise NotImplementedError

    @staticmethod
    def escape(result: str) -> str:
        return result and str(result).strip("\n").strip() or None

    @prompt.register
    def __prompt_for_option(self, query: OptionQuery) -> str:
        option_value = self.option(query.option)
        if not option_value:
            option_value = self.prompt(ValueQuery(question=query.question, default=query.default))

        return self.escape(option_value)

    @prompt.register
    def __prompt_for_boolean(self, query: BooleanQuery) -> bool | Any:
        response = self.escape(self.prompt(ValueQuery(question=query.question, default=query.default)))

        return bool(response.lower() in ("y", "yes", "true", "t", "1"))

    @prompt.register
    def __prompt_for_value(self, query: ValueQuery) -> bool | Any:
        self.io.write(query.question)

        return self.escape(self.io.read_line(default=query.default)) or query.default


class Init(KmsCommand):
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
            """,
        ),
    ]

    def handle(self):
        name = self.prompt(
            OptionQuery(
                "name",
                question="Database name (no spaces): ",
                default="kms",
            )
        )
        database_path = self.prompt(
            OptionQuery(
                "database",
                question="Desired database path: ",
                default=str(self.configuration["database"]["path"]).format(name),
            )
        )

        is_password = self.prompt(BooleanQuery(question="Password protect database? [y/N]: ", default=False))
        password = None
        keyfile = None
        match is_password:
            case True:
                password = self.prompt(ValueQuery(question="Password: ", default=None))
            case False:
                keyfile = self.prompt(
                    OptionQuery(
                        "keyfile",
                        question="Desired keyfile path: ",
                        default=str(self.configuration["keyfile"]["path"]).format("kms"),
                    )
                )

        self.create(dict(database=database_path, password=password, keyfile=keyfile))

    @staticmethod
    def create(database_parameters: dict[str, str | int | bool]) -> None:
        filename = database_parameters["database"]
        os.makedirs(dirname(filename), exist_ok=True)

        kp = PyKeePass(
            filename=filename,
            password=database_parameters["password"],
            keyfile=database_parameters["keyfile"],
        )
        kp.save()


class Add(KmsCommand):
    arguments = []

    def handle(self): ...


class Show(KmsCommand):
    arguments = []

    def handle(self): ...


class Remove(KmsCommand):
    arguments = []

    def handle(self): ...


class Edit(KmsCommand):
    arguments = []

    def handle(self): ...


class Move(KmsCommand):
    arguments = []

    def handle(self): ...


class List(KmsCommand):
    arguments = []

    def handle(self): ...


class Grep(KmsCommand):
    arguments = []

    def handle(self): ...
