from __future__ import annotations

from abc import ABC
from dataclasses import FrozenInstanceError
from typing import Any


class AbstractQuery(ABC):
    def __init__(self, question: str, default: Any = None, init: bool = False):
        self.question = question
        self.default = default
        self.init = init


class FrozenQuery(AbstractQuery):
    def __setattr__(self, key, value):
        if hasattr(self, key):
            raise FrozenInstanceError(f"Cannot assign to field '{key}'")

        super().__setattr__(key, value)


class OptionQuery(FrozenQuery):
    option: str

    def __init__(self, option: str, question: str, default: Any = None, init: bool = False):
        super().__init__(question, default, init)
        self.option = option


class BooleanQuery(FrozenQuery): ...


class ValueQuery(FrozenQuery): ...


class ChoseCredentialsQuery(FrozenQuery): ...


class PasswordQuery(FrozenQuery): ...


class SecretQuery(FrozenQuery): ...

class DatabaseQuery(OptionQuery): ...