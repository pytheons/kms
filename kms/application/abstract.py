import os.path
import re
from abc import abstractmethod

from addict import Dict
from cleo.commands.command import Command
from cleo.helpers import (
    option,
)
from psutil import Process

from kms.application.configuration import Configuration
from kms.application.validators import CredentialsValidator
from kms.domain.enum import PromptKind
from kms.domain.exceptions import UnauthorizedException
from kms.domain.model import (
    BaseCredentials,
    CharactersRule,
    Credentials,
    MinLengthRule,
    ProcessCredentials,
    Prompt,
)


class BaseCommand(Command):
    _default_options = []
    _default_prompts = []
    prompts = []

    def __new__(cls, *args, **kwargs):
        cls.options.extend(cls._default_options)
        cls.prompts.extend(cls._default_prompts)
        return super().__new__(cls)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._prompts = {prompt.name: prompt for prompt in self.prompts}

    def question(self, text: str) -> None:
        self.write(text, "question")

    def prompt(self, name: str):
        prompt: Prompt = self._prompts.get(name)
        question = f"{prompt.question}:"
        if prompt.kind in PromptKind.secured():
            return self.secret(question=question, default=prompt.default) or prompt.default
        return self.ask(question=question, default=prompt.default) or prompt.default


class KmsCommand(BaseCommand):
    configuration = Configuration
    _default_prompts = [
        Prompt(
            name="user",
            kind=PromptKind.SECRET,
            question="Enter the username",
        ),
        Prompt(
            name="password",
            kind=PromptKind.PASSWORD,
            question="Enter the user's password",
        ),
    ]
    _default_options = [
        option(
            "database",
            "d",
            "Specify the path to the database when initializing, accessing or modifying the database. The config is ignored when this is given.",
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
        self.credentials_validator = CredentialsValidator()

        config_password_rules = self.configuration.rules.password
        self.__password_rules = [
            MinLengthRule(config_password_rules.min_length),
            CharactersRule(config_password_rules.characters),
        ]


    def handle(self):
        credentials = self.prompt_credentials()
        if not credentials:
            return

        self(credentials)

    @abstractmethod
    def __call__(self, credentials: Credentials, *args, **kwargs):
        raise NotImplementedError

    @property
    def database(self) -> str:
        return self.configuration.database.path

    @property
    def keyfile(self) -> str:
        return self.configuration.keyfile.path

    @staticmethod
    def is_not_exists(path: str):
        return not os.path.exists(path)

    def prompt_credentials(self):
        os_user = os.getlogin()
        process = Process(os.getppid())

        shells = os.popen("cat /etc/shells").read()
        if process.name() not in shells:
            return ProcessCredentials(user=os_user, name=process.name(), key=self.keyfile)

        user = self.validate_user(os_user)
        password = self.validate_password()

        if not password:
            raise UnauthorizedException("Password is required. Cannot proceed.")

        return BaseCredentials(user, password)

    # def open(self, name: str = "kms") -> SecureStore:
    #     return SecureStore(filename=database_path, password=password, keyfile=keyfile)
    def validate_user(self, os_user):
        user = self.prompt("user")
        if not user:
            raise UnauthorizedException("User not found. Cannot proceed.")
        if user != os_user:
            raise UnauthorizedException("Unauthorized user. User must be the same as os user.")

        return user

    def validate_password(self):
        password = self.prompt("password")
        # for rule in self.__password_rules:
        #     rule.satisfy(password)

        return password