from typing import Type

from cleo.application import Application as Cli
from cleo.commands.command import Command

from kms.application.commands import (
    Add,
    Init,
    KmsCommand,
)
from kms.application.configuration import Configuration
from kms.interface.version import __version__


class KeyManagementService(Cli):
    name: str = "kms"

    def __init__(self):
        super().__init__(self.name, __version__)
        self.configuration = Configuration(self.name)

    @property
    def default_commands(self) -> list[Command]:
        return [*super().default_commands, *[command(self.configuration) for command in self.kms_commands]]

    @property
    def kms_commands(self) -> list[Type[KmsCommand]]:
        return [Init, Add]
