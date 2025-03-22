from abc import (
    ABCMeta,
    abstractmethod,
)


class Handler(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError

class InitializeHandler(Handler):
    def __call__(self, event, context):
        self.setup_configuration()
        self.prompt_for_database()
        self.prompt_for_password()
        self.prompt_for_keyfile()
        self.create()

    def setup_configuration(self): ...

    def prompt_for_database(self): ...

    def prompt_for_password(self): ...

    def prompt_for_keyfile(self): ...

    def create(self): ...


