import json
import os
from abc import ABC
from hashlib import shake_256
from os.path import (
    dirname,
    expanduser,
)
from pathlib import Path

from addict import Dict as Dictionary
from yaml import (
    dump,
    safe_load,
)


class AbstractConfiguration(Dictionary, ABC):
    def to_dict(self) -> dict:
        txt = json.loads(json.dumps(super().to_dict(), default=str))
        return {key: value for key, value in txt.items() if not str(key).startswith("_") and "__" not in key}


class Configuration(AbstractConfiguration):
    __default_configuration: Dictionary

    def __init__(self, filename: str = "kms", *args, **kwargs) -> None:
        default_config_path = "kms/config/default.yaml"
        self.__default_configuration = Dictionary(self.load_file(default_config_path))

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

        self.encryption = self.__default_configuration.encryption

        for key, value in self.__default_configuration.items():
            if key not in ['database', 'keyfile', 'config']:
                setattr(self, key, value)

        self.__secured_path = None
        self.__encrypted_path = None
        self.__decrypted_path = None
        self.__initialize_secured_paths()

    def __initialize_secured_paths(self):
        shake = shake_256()
        shake.update(b"kms")
        app = shake.hexdigest(16)
        self.__secured_path = expanduser(self.__default_configuration.encryption.path).format(app)
        self.encryption.path = self.__secured_path

        shake.update(b"encrypt")
        encrypt = shake.hexdigest(10)
        self.__encrypted_path = f"{self.__secured_path}/.{encrypt}"

        shake.update(b"decrypt")
        decrypt = shake.hexdigest(10)
        self.__decrypted_path = f"{self.__secured_path}/.{decrypt}"


    @property
    def content(self) -> str:
        return self.__default_configuration.keyfile.content

    @staticmethod
    def load_file(path: str) -> dict:
        with open(expanduser(path)) as file:
            return safe_load(file)

    def dump(self) -> None:
        Path(dirname(self.config.path)).mkdir(parents=True, exist_ok=True)
        with open(self.config.path, "w") as file:
            dump(self.to_dict(), file)

    @property
    def encrypted_path(self) -> str:
        return self.__encrypted_path

    @property
    def decrypted_path(self) -> str:
        return self.__decrypted_path