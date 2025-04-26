from functools import singledispatchmethod

from cleo.helpers import (
    argument,
    option,
)

from kms.application.abstract import KmsCommand
from kms.application.validators import CredentialsValidator
from kms.domain.enum import PromptKind
from kms.domain.model import (
    BaseCredentials,
    Credentials,
    InitialCredentials,
    ProcessCredentials,
    Prompt,
)
from kms.infrastructure.adapters import SecureStore


class Init(KmsCommand):
    name = "init"
    options = [
        option(
            "name",
            "N",
            "Specify the name of database when initializing.",
        ),
    ]

    prompts = [
        Prompt(
            name="confirm",
            kind=PromptKind.PASSWORD,
            question="Confirm Password",
        )
    ]

    def __call__(self, credentials: Credentials, *args, **kwargs) -> None:
        if isinstance(credentials, BaseCredentials):
            confirmation = self.prompt("confirm")
            credentials.set(confirm=confirmation)

        self.credentials_validator.validate(credentials)
        # print("Initializing")
        name = self.option("name") or "kms"
        database = self.option("database") or self.database
        keyfile = self.option("keyfile") or self.keyfile

        credentials.set(name=name, database=database, keyfile=keyfile)
        self.create(credentials)
        #     return
        #
        # self.line_error(
        #     "[ ! ] Neither password or keyfile passed for database. No database created.",
        #     style="error",
        # )

    def create(self, credentials: BaseCredentials | ProcessCredentials | InitialCredentials) -> None:

        self.info("Creating database...")
        secure_store = SecureStore(
            filename=credentials.database,
            password=credentials.password,
            keyfile=credentials.keyfile,
        )
        self.info("Creating key...")
        secure_store.create_keyfile(content=self.configuration.content())

        # secure_store.create()
        # self.configuration.dump()

        self.line("Database created. [ <comment>DONE</> ]")




class Add(KmsCommand):
    name = "add"
    options = [
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
        # secure_store = self.open()
        # word = self.option("word")
        # # alphanumeric = self.option("alphanumeric")
        # # symbolic = self.option("symbolic")
        # # append = self.option("append")
        # # fields = self.option("fields")
        group, key = self.extract_group_from_path()
        #
        # if group:
        # secure_store.add_group(group)

        # if key:
        # value = self.prompt(SecretQuery(question="Secret: ", default=None))
        # secure_store.add_entry(group, key, value)

        # secure_store.save(secure_store.filename)

    def extract_group_from_path(self):
        path = self.argument("PATH")
        group, *entry = path and path.strip("/").split("/")
        if group and not entry:
            entry = [group]
            group = None

        key = "/".join(entry)
        return group, key


class Show(KmsCommand):
    def __call__(self, *args, **kwargs):
        pass

    name = "show"
    arguments = []

    # def handle(self):
    #     secure_store = self.open()
    #     print(secure_store.find_entries())


class Remove(KmsCommand):
    arguments = []

    # def handle(self): ...
