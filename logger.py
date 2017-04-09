from __future__ import print_function
import inspect
import traceback

from config import config

# fastlogin exception
from message import Message


class FastLoginLogger:
    def __init__(self):
        self.__debug = config.get_boolean("debug")

    def __print(self, color, message, *args):
        if message:
            if len(args):
                message = Message.format(message, *args)
            if color:
                print("\033[" + str(color) + "m" + message + "\033[0m")
            else:
                print (message)

    def debug_on(self):
        self.__debug = True

    def info(self, message, *args):
        self.__print(None, message, *args)

    def tips(self, message, *args):
        self.__print(32, message, *args)

    def error(self, message, *args):
        self.__print(31, message, *args)

    def debug(self, message, *args):
        if self.__debug and message:
            self.info(message, *args)

    def exception(self, message=None, *args):
        if self.__debug:
            self.error("\nx" + traceback.format_exc())
        else:
            self.error(message, *args)


log = FastLoginLogger()

if __name__ == '__main__':

    try:
        raise Exception("error")
    except:
        frame = inspect.getframeinfo(inspect.currentframe())
        log.exception("error at file {}, line {}", frame.filename, frame.lineno)

