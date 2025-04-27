from enum import (
    Enum,
    auto,
)

class AutoNamed(Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values) -> str:
        return name

class PromptKind(Enum):
    SECRET = auto()
    PASSWORD = auto()

    @classmethod
    def secured(cls):
        return [cls.SECRET, cls.PASSWORD]
