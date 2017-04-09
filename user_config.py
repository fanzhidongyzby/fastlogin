import os
import pickle

from logger import log


# user's config
class UserConfig:
    def __init__(self):
        self.directory = os.path.expanduser("~") + "/.fastlogin"
        self.tmp_directory = self.directory + "/tmp"

        self.__ensure_directories(self.directory, self.tmp_directory)

        self.login_info_file = self.directory + "/logininfo.pickle"
        self.white_list_file = self.directory + "/whitelist.pickle"

        self.__ensure_files(self.login_info_file, self.white_list_file)

    def __ensure_directories(self, *directories):
        for directory in directories:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory, 0700)
                except:
                    log.exception("directory {} create failed", directory)
            if os.stat(directory).st_mode & 0777 != 0700:
                os.chmod(directory, 0700)
                log.debug("chmod 0700 to directory {}", directory)

    def __ensure_files(self, *files):
        for file in files:
            if not os.path.exists(file):
                try:
                    open(file, "w").close()
                except:
                    log.exception("file {} create failed", file)
            if os.stat(file).st_mode & 0777 != 0600:
                os.chmod(file, 0600)
                log.debug("chmod 0600 to file {}", file)

    def read(self, file_name, type=None):
        default = type() if type else None
        try:
            if os.stat(file_name).st_size == 0:
                return default
            else:
                with open(file_name, "rb") as fp:
                    pickle_file = pickle.load(fp)
                    if pickle_file != None and (type == None or isinstance(pickle_file, type)):
                        return pickle_file
                    else:
                        return default
        except:
            log.exception()

    def write(self, file_name, value):
        try:
            with open(file_name, "wb") as fp:
                pickle.dump(value, fp)
                fp.flush()
                return True
        except:
            log.exception()

        return False


user_config = UserConfig()
