import os.path
from functools import singledispatchmethod
from typing import (
    Any,
)

from cleo.commands.command import Command
from cleo.helpers import (
    argument,
    option,
)

from kms.application.configuration import Configuration
from kms.application.queries import (
    AbstractQuery,
    BooleanQuery,
    ChoseCredentialsQuery,
    DatabaseQuery,
    OptionQuery,
    PasswordQuery,
    SecretQuery,
    ValueQuery,
)
from kms.infrastructure.adapters import KeePassXC


class BaseCommand(Command):
    _default_options = []

    def __new__(cls, *args, **kwargs):
        cls.options.extend(cls._default_options)
        return super().__new__(cls)

    def question(self, text: str) -> None:
        self.write(text, "question")


class KmsCommand(BaseCommand):
    configuration = Configuration
    _default_options = [
        option(
            "database",
            "d",
            "Specify the path to the KeePass database when initializing, accessing or modifying the database. The config is ignored when this is given.",
        ),
        option(
            "keyfile",
            "k",
            "Specify the path to the keyfile when initializing, accessing or modifying the database.",
        ),
        option(
            "config",
            "c",
            "Specify the path to the config file when initializing, accessing or modifying the database.",
        ),
    ]

    def __init__(self, configuration: Configuration) -> None:
        super().__init__()
        self.configuration = configuration

    @singledispatchmethod
    def prompt(self, query: AbstractQuery) -> Any:
        raise NotImplementedError

    @prompt.register
    def __prompt_for_option(self, query: OptionQuery) -> str:
        option_value = self.option(query.option)
        if not option_value and query.init:
            option_value = self.prompt(ValueQuery(question=query.question, default=query.default))

        return self.escape(option_value) or query.default

    @prompt.register
    def __prompt_for_database(self, query: DatabaseQuery) -> str:
        return self.prompt(
            OptionQuery(
                option=query.option,
                question=query.question,
                default=query.default,
                init=query.init,
            )
        )

    @property
    def database(self) -> str:
        return self.configuration.database.path

    @property
    def keyfile(self) -> str:
        return self.configuration.keyfile.path

    @staticmethod
    def is_not_exists(path: str):
        return not os.path.exists(path)

    @prompt.register
    def __prompt_for_boolean(self, query: BooleanQuery) -> bool | Any:
        response = self.escape(self.prompt(ValueQuery(question=query.question, default=query.default)))

        return bool(response and response.lower() in ("y", "yes", "true", "t", "1"))

    @prompt.register
    def __prompt_for_value(self, query: ValueQuery) -> bool | Any:
        return self.ask(query.question) or query.default

    @prompt.register
    def __prompt_for_credentials(self, query: ChoseCredentialsQuery) -> bool | Any:
        password = None
        keyfile = None
        is_password = False

        if query.init:
            is_password = self.prompt(BooleanQuery(question=query.question, default=query.default))

        match is_password:
            case True:
                password = self.prompt(PasswordQuery(question="Password:", default=None))
            case False:
                keyfile = self.prompt(
                    OptionQuery(
                        "keyfile",
                        question="Desired keyfile path: ",
                        default=("{}" in self.keyfile and self.keyfile.format("kms")) or self.keyfile,
                        init=query.init,
                    )
                )

        return password, keyfile

    @prompt.register
    def __prompt_for_password(self, query: PasswordQuery) -> bool | Any:
        password = self.secret(question=query.question, default=query.default)
        confirm = self.secret(question=f"Confirm {query.question.lower()}", default=query.default)
        if password != confirm:
            self.line_error("ERROR: Passwords do not match", style="error")
            return False

        return password

    @prompt.register
    def __prompt_for_secret(self, query: SecretQuery) -> bool | Any:
        return self.secret(question=query.question, default=None)

    @staticmethod
    def escape(result: str) -> str:
        return result and str(result).strip("\n\n").strip() or None

    def open(self, name: str = "kms") -> KeePassXC:
        database_path, password, keyfile = self.prompt_default_options(name)
        return KeePassXC(
            filename=database_path,
            password=password,
            keyfile=keyfile,
            readonly=True,
        )

    def prompt_default_options(
        self,
        name: str = "kms",
        init: bool = False,
    ):
        database_path = self.prompt(
            DatabaseQuery(
                "database",
                question="Desired database path: ",
                default=("{}" in self.database and self.database.format(name)) or self.database,
                init=init,
            )
        )

        password, keyfile = self.prompt(
            ChoseCredentialsQuery(
                question="Password protect database? [y/N]: ",
                default=False,
                init=init,
            ),
        )

        return database_path, password, keyfile


class Init(KmsCommand):
    name = "init"
    options = [
        option(
            "name",
            "N",
            "Specify the name of KeePass database when initializing.",
        ),
    ]

    def handle(self):
        name = self.prompt(
            OptionQuery(
                "name",
                question="Database name (no spaces): ",
                default="kms",
                init=True
            )
        )

        database_path, password, keyfile = self.prompt_default_options(name, init=True)

        if any([password, keyfile]):
            self.create(dict(database=database_path, password=password, keyfile=keyfile))
            return

        self.line_error(
            "[ ! ] Neither password or keyfile passed for database. No database created.",
            style="error",
        )

    def create(self, database_parameters: dict[str, str | int | bool]) -> None:
        self.info("Creating database...")
        kee_pass_xc = KeePassXC(
            filename=database_parameters["database"],
            password=database_parameters["password"],
            keyfile=database_parameters["keyfile"],
        )
        if kee_pass_xc.keyfile:
            kee_pass_xc.create_keyfile(content=self.configuration.content())

        kee_pass_xc.create()
        self.configuration.dump()

        self.line("Database created. [ <comment>DONE</> ]")


class Add(KmsCommand):
    name = "add"
    options = [
        option(
            "username",
            "u",
            """Username is used by password store in database entry.""",
        ),
        option(
            "word",
            "w",
            """Words size for generate secret or password. Defaults to 5.""",
        ),
        option(
            "alphanumeric",
            "a",
            """Length of alphanumeric characters. Defaults to 32.""",
        ),
        option(
            "symbolic",
            "s",
            """Length of symbolic characters. Defaults to 32.""",
        ),
        option(
            "append",
            None,
            "Use --append to append STR to the end of the generated secret to meet specific password requirements.",
        ),
        option(
            "fields",
            "f",
            "Use --fields to specify a comma separated list of custom fields to prompt for during entry creation." "",
        ),
    ]
    arguments = [
        argument("PATH", "The full path to the entry or group"),
    ]

    def handle(self):
        kee_pass_xc = self.open()
        # word = self.option("word")
        # # alphanumeric = self.option("alphanumeric")
        # # symbolic = self.option("symbolic")
        # # append = self.option("append")
        # # fields = self.option("fields")
        group, key = self.extract_group_from_path()
        #
        if group:
            kee_pass_xc.add_group(group, group)
        #
        if key:
            value = self.prompt(SecretQuery(question="Secret: ", default=None))
            username = self.option("username") or key
            kee_pass_xc.add_entry([], key, username=username, password=value)

    def extract_group_from_path(self):
        path = self.argument("PATH")
        group, *entry = path and path.strip("/").split("/")
        if group and not entry:
            entry = [group]
            group = None

        key = "/".join(entry)
        return group, key


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


class UnsealVault(KmsCommand):
    arguments = []

    def handle(self): ...
