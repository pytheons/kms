import hashlib
import os
from os.path import expanduser

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

from kms.infrastructure.decorator import mkdir


class SecureStore:
    def __init__(self, filename, password=None, keyfile=None):
        self._filename = filename and str(os.path.expanduser(filename))
        self._password = password
        self._keyfile = keyfile and str(os.path.expanduser(keyfile))
        self.__key_pairs = None

    @property
    def keyfile(self):
        return self._keyfile

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value: str):
        if self._filename:
            return

        self._filename = value

    @mkdir
    def create(self): ...

    @mkdir
    def create_encryption(self):
        self.__key_pairs = RSA.generate(4096)
        directory = os.path.dirname(self.keyfile)

        private_pem = self.__key_pairs
        with open(f"{directory}/private.pem", "w") as private_file:
            private_file.write(private_pem.export_key().decode())

        public_pem = self.__key_pairs.publickey()
        with open(f"{directory}/public.pem", "w") as pu:
            pu.write(public_pem.export_key().decode())

    @mkdir
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
