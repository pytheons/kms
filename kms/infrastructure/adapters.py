import os
from os.path import dirname

from pykeepass import (
    PyKeePass,
    create_database,
)


class KeePassXC(PyKeePass):
    def __init__(self, filename, password=None, keyfile=None, transformed_key=None, decrypt=True):
        os.makedirs(dirname(filename), exist_ok=True)
        create_database(filename, password=password, keyfile=keyfile, transformed_key=transformed_key)
        super().__init__(filename, password, keyfile, transformed_key, decrypt)
