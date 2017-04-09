import ConfigParser


# ignore section in config.properties file
class FileWithSection(object):
    def __init__(self, fp):
        self.fp = fp
        self.section = "[" + ConfigParser.DEFAULTSECT + "]\n"

    def readline(self):
        if self.section:
            try:
                return self.section
            finally:
                self.section = None
        else:
            return self.fp.readline()


# config.properties file
class Config:
    CONFIG_FILE = "config.properties"

    def __init__(self):
        self.config = ConfigParser.SafeConfigParser()
        self.config.readfp(FileWithSection(open(Config.CONFIG_FILE)))

    def get_string(self, key, option=""):
        result = option
        try:
            result = self.config.get(ConfigParser.DEFAULTSECT, key)
        finally:
            return result

    def get_boolean(self, key, option=False):
        result = option
        try:
            result = self.config.getboolean(ConfigParser.DEFAULTSECT, key)
        finally:
            return result

    def get_int(self, key, option=0):
        result = option
        try:
            result = self.config.getint(ConfigParser.DEFAULTSECT, key)
        finally:
            return result

    def get_float(self, key, option=0.0):
        result = option
        try:
            result = self.config.getfloat(ConfigParser.DEFAULTSECT, key)
        finally:
            return result


config = Config()
