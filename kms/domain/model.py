import re
from abc import (
    ABCMeta,
    abstractmethod,
)
from dataclasses import (
    dataclass,
    field,
)
from typing import Any,\
    List

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


class Rule(metaclass=ABCMeta):
    @abstractmethod
    def satisfy(self, value: Any):
        raise NotImplementedError


class MinLengthRule(Rule):
    def __init__(self, min_length: int):
        self.min_length = min_length

    def satisfy(self, value: Any):
        assert len(str(value)) == self.min_length, "Not a valid length"

class CharactersRule(Rule):
    def __init__(self, patterns: List[str]):
        self.patterns = patterns

    def satisfy(self, value: Any):
        stringify_value = str(value)
        for character_pattern in self.patterns:
            if "{[()]}" == character_pattern:
                character_pattern = "".join([f"\\{character}" for character in character_pattern])
            assert re.match(f".*[{character_pattern}].*", stringify_value), f"Not a valid pattern {character_pattern}"

class SecuredDatabase(Dict):
    def __init__(self):
        self.users = Dict()
        self.namespaces = Dict()
