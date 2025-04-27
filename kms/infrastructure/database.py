import hashlib
import os
from os.path import (
    dirname,
    expanduser,
)

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

from kms.application.configuration import Configuration
from kms.domain.model import ProcessCredentials, BaseCredentials, InitialCredentials

Credentials = ProcessCredentials | BaseCredentials | InitialCredentials

class SecureStore:
    def __init__(self, credentials: Credentials, config: Configuration) -> None:
        self.__config = config
        self.__keyfile = credentials.keyfile and str(expanduser(credentials.keyfile))
        self.__filename = credentials.database and str(expanduser(credentials.database))
        self.__key_pairs = None
        paths = [self.keyfile, self.filename, self.__config.encrypted_path, self.__config.encrypted_path]
        for path in paths:
            os.makedirs(dirname(path), exist_ok=True)

    @property
    def keyfile(self):
        return self.__keyfile

    @property
    def filename(self):
        return self.__filename

    def create(self): ...

    def create_keyfile(self, content: str):
        self.create_encryption()
        public_key = self.__key_pairs.publickey()

        with open(expanduser(self.keyfile), "wb") as keyfile:
            sha = hashlib.sha3_512()
            sha.update(os.urandom(512))
            key = sha.hexdigest()
            file_content = str(content).format(key)
            cipher = PKCS1_OAEP.new(public_key)
            file_content = cipher.encrypt(bytes(file_content, "utf-8"))
            keyfile.write(file_content)

    def create_encryption(self):
        self.__key_pairs = RSA.generate(4096)
        private_pem = self.__key_pairs
        with open(self.__config.decrypted_path, "w") as private_file:
            private_file.write(private_pem.export_key().decode())

        public_pem = self.__key_pairs.publickey()
        with open(self.__config.encrypted_path, "w") as pu:
            pu.write(public_pem.export_key().decode())
