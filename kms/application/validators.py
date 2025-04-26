from abc import ABCMeta,\
    abstractmethod
from functools import singledispatchmethod

from kms.domain.model import BaseCredentials,\
    Credentials


class Validator(metaclass=ABCMeta):
    @abstractmethod
    def validate(self, credentials: Credentials):
        raise NotImplementedError

class CredentialsValidator(Validator):
    @singledispatchmethod
    def validate(self, credentials: Credentials) -> Credentials:
        raise NotImplementedError

    @validate.register
    def validate_password(self, credentials: BaseCredentials) -> Credentials:
        assert credentials.password == credentials.confirm, "[ ERROR ] Password does not match."
        return credentials