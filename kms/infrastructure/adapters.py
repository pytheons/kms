import os
from base64 import b64encode
from os.path import expanduser

from pykeepass import (
    PyKeePass,
    create_database,
)

from kms.infrastructure.decorator import mkdir


class KeePassXC(PyKeePass):
    def __init__(self, filename, password=None, keyfile=None, transformed_key=None, decrypt=True, readonly=False):
        self._filename = filename and str(os.path.expanduser(filename))
        self._password = password
        self._keyfile = keyfile and str(os.path.expanduser(keyfile))
        self._transformed_key = transformed_key
        self._decrypt = decrypt

        if os.path.exists(self.filename) and readonly:
            super().__init__(self.filename, password, keyfile, transformed_key, decrypt)

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value: str):
        if not self._filename:
            self._filename = value

    @mkdir
    def create(self):
        create_database(
            filename=self._filename,
            password=self._password,
            keyfile=self._keyfile,
            transformed_key=self._transformed_key,
        )

    @mkdir
    def create_keyfile(self, content: str):
        with open(expanduser(self.keyfile), "w") as keyfile:
            file_content = str(content).format(b64encode(os.urandom(64)).decode())
            keyfile.write(file_content)
