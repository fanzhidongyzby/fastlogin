from __future__ import print_function
import commands
import os
import sys

from config import config
from logger import log
from login_info import login_info, LoginRecord
from message import Message
from white_list import white_list


class FastLogin:
    def __init__(self, args):
        self.ssh_keep_alive = config.get_string("ssh.keep.alive", "72h")

        self.option_values = self.__parse_args(args)

        self.host, self.user, self.password = self.__read_values("", 3)
        self.proxy_host, self.proxy_user = self.__read_values("-p", 2)
        self.proxy_password = None
        (self.password_suffix) = self.__read_values("-s", 1)
        self.show_info = self.__read_values("-i", 0) or self.__read_values("-I", 0)
        self.remove_host, self.remove_user = self.__read_values("-i-", 2)
        self.show_password = self.__read_values("-I", 0)
        self.show_white_list = self.__read_values("-w", 0)
        self.add_white_list = self.__read_values("-w+", 1)
        self.remove_white_list = self.__read_values("-w-", 1)
        self.debug_on = self.__read_values("-D", 0)
        self.show_help = self.__read_values("-h", 0)
        self.show_version = self.__read_values("-v", 0)

    # parse command line
    def __parse_args(self, args):
        option_values = {}

        if not args:
            return option_values

        option_indices = []
        for (index, arg) in enumerate(args):
            if index == 0 or arg.startswith("-"):
                option_indices.append(index)

        for (i, option_index) in enumerate(option_indices):
            option = "" if option_index == 0 else args[option_index]
            next_index = option_indices[i + 1] if i + 1 < len(option_indices) else len(args)
            value = args[option_index + 1:next_index]
            option_values[option] = value
        return option_values

    # retrieve args
    def __list_to_tuple(self, values, length):
        list_values = []
        for i in range(length):
            if i < len(values):
                list_values.append(values[i])
            else:
                list_values.append(None)
        return tuple(list_values)

    # retrieve args by key
    def __read_values(self, key, count):
        if count == 0:
            return key in self.option_values
        values = self.option_values[key] if key in self.option_values else []
        tuple_values = self.__list_to_tuple(values, count)
        if count == 1:
            return tuple_values[0]
        else:
            return tuple_values

    def run(self):
        if self.debug_on:
            log.debug_on()
        if self.show_help:
            log.info("FastLogin:\n"
                     "\tx host [user] [password] [option [value]*]\n"
                     "options:\n"
                     "\t-p <host> [<user>]\tSpecify proxy host and user\n"
                     "\t-s <suffix>\t\tPassword suffix (proxy use first)\n"
                     "\t-i\t\t\tShow detail login info\n"
                     "\t-i- <host> [<user>]\tRemove host or user info\n"
                     "\t-I\t\t\tShow detail login info \033[31m(see password)\033[0m\n"
                     "\t-w\t\t\tShow white list config\n"
                     "\t-w+ <host>\t\tAdd white list record\n"
                     "\t-w- <host>\t\tRemove white list record\n"
                     "\t-D\t\t\tTurn debug on\n"
                     "\t-h\t\t\tShow this help message\n"
                     "\t-v\t\t\tShow version\n"
                     )
        elif self.show_version:
            log.tips("FastLogin V1.0.0 Author: Florian alibaba.inc\n"
                     "FastLogin is a SSH tool which can help you:\n"
                     "  1. Record login host, user and password.\n"
                     "  2. Fast pattern match to fill login info.\n"
                     "  3. Dynamic token support with password suffix.\n"
                     "  4. Proxy login support.\n"
                     "  5. White list support to avoid login info auto-removed.\n"
                     "  6. SSH channel reuse.\n"
                     )
        elif self.show_info:
            info = login_info.color_string(self.show_password)
            if info:
                log.info("Detail login records:")
                log.info(info)
        elif self.show_white_list:
            config = white_list.get()
            if config:
                log.info("White list config:")
                log.tips("\n".join(config))
            else:
                log.info("White list is empty")
        elif self.remove_host:
            ok = login_info.remove_host_or_user(self.remove_host, self.remove_user)
            login_info.save()
            if ok:
                if self.remove_user:
                    log.tips("Login record of user {}@{} removed",
                             self.remove_user, self.remove_host)
                else:
                    log.tips("Login records of host {} removed", self.remove_host)
        elif self.add_white_list:
            white_list.add(self.add_white_list)
            white_list.save()
            log.tips("White list record '{}' added", self.add_white_list)
        elif self.remove_white_list:
            white_list.remove(self.remove_white_list)
            white_list.save()
            log.tips("White list record '{}' removed", self.remove_white_list)
        elif not self.host:
            # show all hosts
            hosts = login_info.get_hosts()
            if hosts:
                log.info("Following hosts can be fast login:")
                log.tips("\n".join(hosts))
        else:
            self.__login()

    def __login(self):
        # search login record
        record = login_info.search(self.host, self.user)
        if not record:
            return

        # process record
        record.password = self.password or record.password or login_info.force_read("password", True)
        if not record.password:
            return
        self.host, self.user, self.password = record.host, record.user, record.password

        # process proxy
        proxy = None
        (self.proxy_host, self.proxy_user) = (self.proxy_host, self.proxy_user) \
            if self.proxy_host else (record.proxy_host, record.proxy_user)
        if self.proxy_host:
            proxy = login_info.search(self.proxy_host, self.proxy_user)
            if not LoginRecord.valid(proxy):
                log.error("Proxy {}@{} has not been login", self.proxy_user, self.proxy_host)
                return
            self.proxy_host, self.proxy_user = proxy.host, proxy.user
            record.proxy_host, record.proxy_user = proxy.host, proxy.user

        # process suffix
        if proxy:
            record.use_password_suffix = False
            proxy.use_password_suffix = not not self.password_suffix
            self.proxy_password = proxy.password \
                if not self.password_suffix else proxy.password + self.password_suffix
        else:
            record.use_password_suffix = not not self.password_suffix
            self.password = record.password \
                if not self.password_suffix else record.password + self.password_suffix

        # ssh login
        cmd = Message.format("expect ssh-expect {} {} {} {} {} {} {} 2>/dev/null",
                             self.host, self.user, self.password,
                             proxy and self.proxy_host or "",
                             proxy and self.proxy_user or "",
                             proxy and self.proxy_password or "",
                             self.ssh_keep_alive
                             )
        code = os.system(cmd)
        try:
            if code == 0:
                login_info.add(record)
            else:
                login_info.remove(record)
                if os.system("which pbcopy &> /dev/null") == 0:
                    cmd = Message.format("bash -c 'echo -n x {} {} {}{}{}' | pbcopy",
                                         record.host, record.user, record.password,
                                         proxy and Message.format(" -p {} {}", proxy.host, proxy.user) or "",
                                         not not self.password_suffix
                                         and Message.format(" -s {}", self.password_suffix) or ""
                                         )

                    commands.getstatusoutput(cmd)
                    print("Fast Login failed, login info has been copied, use Ctrl + V to try again.")
        finally:
            login_info.save()


if __name__ == '__main__':
    fast_login = FastLogin(sys.argv)
    fast_login.run()
