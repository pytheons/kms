from cleo.application import Application

from kms.interface.cli import KeyManagementService

def cli():
    KeyManagementService().run()