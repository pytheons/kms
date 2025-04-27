import os

from cleo.helpers import (
    argument,
    option,
)

from kms.application.abstract import KmsCommand
from kms.domain.enum import PromptKind
from kms.domain.exceptions import DatabaseExistsException
from kms.domain.model import (
    BaseCredentials,
    Credentials,
    InitialCredentials,
    ProcessCredentials,
    Prompt,
)
from kms.infrastructure.database import SecureStore


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
        ),
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

    def create(self, credentials: BaseCredentials | ProcessCredentials | InitialCredentials) -> None:
        secure_store = SecureStore(credentials=credentials, config=self.configuration)

        self.write("<info>[ 1 ] Creating configuration...")
        self.configuration.dump()
        self.line(" [ <comment>DONE</> ]</>")

        self.write("<info>[ 2 ] Generating keys...")
        if os.path.exists(credentials.keyfile):
            raise DatabaseExistsException("Database already exists. Cannot proceed.")
        secure_store.create_keyfile(content=self.configuration.content)
        self.line(" [ <comment>DONE</> ]</>")

        self.write("<info>[ 3 ] Creating database...")
        secure_store.create()
        self.line(" [ <comment>DONE</> ]</>\n")
        self.line("Database initialized successfully.")


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
