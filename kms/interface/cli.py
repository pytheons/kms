from cleo.application import Application as Cli
from cleo.commands.command import Command
from kms.application.commands import Init
from kms.application.configuration import KMSConfiguration
from kms.application.handlers import InitializeHandler
from kms.interface.version import __version__


class KeyManagementService(Cli):

    def __init__(self):
        super().__init__("kms", __version__)
        self.configuration = KMSConfiguration("kms", )

    @property
    def default_commands(self) -> list[Command]:
        return [
            *super().default_commands,
            Init(handler=InitializeHandler()),
        ]
