import json
import os
from abc import ABC
from os.path import (
    dirname,
    exists,
    expanduser,
)
from pathlib import Path

from addict import Dict as Dictionary
from yaml import dump, \
    safe_load


class AbstractConfiguration(Dictionary, ABC):
    def to_dict(self) -> dict:
        txt = json.loads(json.dumps(super().to_dict()))
        return {key: value for key, value in txt.items() if not str(key).startswith("_") and "__" not in key}


class Configuration(AbstractConfiguration):
    __default_configuration: Dictionary

    def __init__(self, filename: str = "kms", *args, **kwargs) -> None:
        default_path = f"{filename}/config/default.yaml"
        self.__default_configuration = Dictionary(self.load_file(default_path))

        config_path = expanduser(self.__default_configuration.config.path)
        if os.path.exists(config_path):
            config_file = Dictionary(self.load_file(config_path))
            for key, value in config_file.items():
                setattr(self, key, value)
            return

        self.database = self.__default_configuration.database
        self.database.path = expanduser(self.database.path).format(filename)
        self.keyfile = Dictionary()
        self.keyfile.path = expanduser(self.__default_configuration.keyfile.path).format(filename)

        self.config = self.__default_configuration.config
        self.config.path = expanduser(self.config.path)

    def content(self):
        return self.__default_configuration.keyfile.content

    @staticmethod
    def load_file(path: str):
        with open(expanduser(path)) as file:
            return safe_load(file)

    def dump(self):
        Path(dirname(self.config.path)).mkdir(parents=True, exist_ok=True)
        with open(self.config.path, "w") as file:
            dump(self.to_dict(), file)
