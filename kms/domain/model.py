from abc import ABCMeta
from dataclasses import (
    dataclass,
    field,
)
from typing import Any

from addict import Dict

from kms.domain.enum import PromptKind


class Prompt:
    def __init__(self, name: str, kind: PromptKind, question: str, default: Any = None, **kwargs):
        self.name = name
        self.kind = kind
        self.question = question
        self.options = Dict(**kwargs)
        self.default = default

class Credentials(metaclass=ABCMeta):
    def set(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

@dataclass
class BaseCredentials(Credentials):
    user: str
    password: str
    confirm: str | None = field(init=False)

@dataclass
class ProcessCredentials(Credentials):
    user: str
    name: str
    key: str

@dataclass
class InitialCredentials(Credentials):
    name: str
    database: str
    keyfile: str