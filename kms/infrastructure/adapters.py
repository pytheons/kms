import os
from base64 import b64encode
from functools import wraps
from os.path import dirname, \
    expanduser

from confuse import Subview
from pykeepass import (
    PyKeePass,
    create_database,
)

from kms.infrastructure.decorator import mkdir


class KeePassXC(PyKeePass):
    def __init__(self, filename, password=None, keyfile=None, transformed_key=None, decrypt=True):
        self._filename = filename and str(os.path.expanduser(filename))
        self._password = password
        self._keyfile = keyfile and str(os.path.expanduser(keyfile))
        self._transformed_key = transformed_key
        self._decrypt = decrypt

        if os.path.exists(self._filename):
            super().__init__(filename, password, keyfile, transformed_key, decrypt)

    @property
    def filename(self):
        return self._filename

    @mkdir
    def create(self):
        create_database(
            filename=self._filename,
            password=self._password,
            keyfile=self._keyfile,
            transformed_key=self._transformed_key,
        )

    @mkdir
    def create_keyfile(self, content: str | Subview):
        if isinstance(content, Subview):
            content = str(content)
        with open(self.keyfile, "w") as keyfile:
            file_content = content.format(b64encode(os.urandom(64)).decode())
            keyfile.write(file_content)

