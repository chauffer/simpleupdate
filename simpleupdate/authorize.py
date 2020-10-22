import re
from dataclasses import dataclass

import bcrypt

from .settings import SIMPLEUPDATE_DEFAULT_REGEX


class Authorize:
    _config = []

    def __init__(self, config_file_path):
        self.config_file_path = config_file_path

    @property
    def config(self):
        if self._config:
            return self._config

        with open(self.config_file_path) as f:
            config_content = f.readlines()
        for line in config_content:
            row = line.split()
            self._config.append(
                ConfigRow(
                    row[0],
                    row[1].split("/")[0],
                    row[1].split("/")[1],
                    SIMPLEUPDATE_DEFAULT_REGEX if len(row) < 3 else row[2],
                )
            )
        return self._config


    def is_authorized(self, token, namespace, deployment, tag=None):
        matching_configrows = [
            row for row in self.config
            if row.namespace == namespace and row.deployment == deployment
        ]

        for row in matching_configrows:
            if bcrypt.checkpw(token.encode(), row.btoken.encode()):
                if tag and not len(re.findall(row.allowed_regex, tag)):
                    return False

                return True

        return False

@dataclass
class ConfigRow:
    btoken: str
    namespace: str
    deployment: str
    allowed_regex: str
