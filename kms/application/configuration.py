import os

from confuse import (
    Configuration,
    yaml_util,
)


class KMSConfiguration(Configuration):
    __default_configuration: Configuration

    def __init__(self, appname, modname=None, read=True, loader=yaml_util.Loader):
        super().__init__(appname, modname, read, loader)
        self.__default_configuration = Configuration(appname)
        self.__default_configuration.set_file("kms/config/default.yaml", base_for_paths=True)

        self["database"] = self.__default_configuration["database"]
        self["keyfile"] = self.__default_configuration["keyfile"]

        default_config = self.__default_configuration["config"]
        self["config"] = default_config

        if os.path.exists(os.path.expanduser(default_config["path"].as_str())):
            self.set_file(default_config["path"], base_for_paths=True)