from logger import log
from user_config import user_config


# white list
class WhiteList:
    def __init__(self):
        self.config = user_config.read(user_config.white_list_file, list)

    def save(self):
        if user_config.write(user_config.white_list_file, self.config):
            log.debug("white list updated")
        else:
            log.debug("white list update failed")

    def get(self):
        self.config.sort()
        return self.config

    def add(self, record):
        if isinstance(record, str) and record:
            if record not in self.config:
                self.config.append(record)
        else:
            log.debug("record {} is not type {}", record, str)

    def remove(self, record):
        if isinstance(record, str) and record and record in self.config:
            self.config.remove(record)
        else:
            log.debug("record {} is not type {}", record, str)

    def clear(self):
        self.config = []

    def __contains__(self, item):
        return self.config and item in self.config

white_list = WhiteList()