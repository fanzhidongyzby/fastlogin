import sys
import os
import shutil
import traceback
import commands
import base64


class WhiteList:
    WHITE_LIST_CONFIG = os.path.expanduser("~") + "/.fastlogin.whitelist"

    def __init__(self):
        self.config = []
        try:
            with open(WhiteList.WHITE_LIST_CONFIG, "r") as config_file:
                lines = config_file.readlines()
                for line in lines:
                    if line:
                        self.config.append(line.strip())
        except:
            pass

    def __contains__(self, item):
        return self.config and item in self.config


class LoginInfo:
    CACHE_FILE = os.path.expanduser("~") + "/.fastlogin.info"
    CACHE_FILE_TMP = CACHE_FILE + ".tmp"
    MAX_LINE_COUNT = 100
    DEBUG = False

    def __process_exception(self):
        if self.DEBUG:
            print traceback.format_exc()
        else:
            pass

    def __init__(self):
        os.system("touch " + LoginInfo.CACHE_FILE)
        self.password_changed = False
        self.host_map = {}
        self.whitelist = WhiteList()

    def __parse(self, lines):
        host_map = {}
        lines = lines[-LoginInfo.MAX_LINE_COUNT:]
        for line in lines:
            cols = line.split()
            if len(cols) != 3:
                continue
            (host, user, password) = (cols[0], cols[1], cols[2])
            if not host_map.has_key(host):
                host_map[host] = {}
            host_map[host][user] = base64.decodestring(password)
            self.host_map = host_map

    def search(self, host, user, password):
        if not host:
            return (None, None, None)
        try:
            with open(LoginInfo.CACHE_FILE, "r") as cache:
                # load login info
                self.__parse(cache.readlines())
        except:
            self.__process_exception()

        host_map = self.host_map

        # match host
        choose_host = None
        matched_hosts = filter(
            lambda h: h.find(host) != -1 if host else False,
            host_map.keys()
        )
        if len(matched_hosts) > 1:
            print "Following hosts were found:"
            for index, item in enumerate(matched_hosts):
                print "\t {0}: {1}".format(index + 1, item)
            try:
                choose = int(raw_input("Choose one to continue: ").strip())
                choose_host = matched_hosts[choose - 1]
            except:
                self.__process_exception()
        else:
            choose_host = matched_hosts[0] if matched_hosts else host

        # choose user
        choose_user = None
        if choose_host:
            if not host_map.has_key(choose_host):
                host_map[host] = {}
            if user:
                choose_user = user
            else:
                matched_users = host_map[choose_host].keys()
                if len(matched_users) > 1:
                    print "Following users / password were found:"
                    for index, item in enumerate(matched_users):
                        print "\t {0}: {1} / {2}".format(index + 1, item, host_map[choose_host][item])
                    try:
                        choose = int(raw_input("Choose one to continue: ").strip())
                        choose_user = matched_users[choose - 1]
                    except:
                        self.__process_exception()
                else:
                    if matched_users:
                        choose_user = matched_users[0]

            # choose password
            if choose_user:
                if not host_map[choose_host].has_key(choose_user):
                    if not password:
                        print "Password of {1}@{0} must be set.".format(choose_host, choose_user)
                        sys.exit(1)
                    host_map[choose_host][choose_user] = password
                choose_password = host_map[choose_host][choose_user]
                if password and choose_password != password:
                    self.password_changed = True
                    host_map[choose_host][choose_user] = password
                return (choose_host, choose_user, host_map[choose_host][choose_user])
            else:
                print "No user has been choose."
                sys.exit(1)
        else:
            print "No host has been choose."
            sys.exit(1)

    def try_remove(self, host0, user0, password0):
        host_map = self.host_map

        for (host, user_map) in host_map.items():
            if host in self.whitelist:
                continue
            for (user, password) in user_map.items():
                if host == host0 and user == user0 and password == password0:
                    if len(host_map[host]) == 1:
                        # only one record, remove host
                        del host_map[host]
                    else:
                        # only remove the user item
                        del host_map[host][user]

                    # refresh config
                    self.save()
                    return

    def save(self):
        host_map = self.host_map

        try:
            with open(LoginInfo.CACHE_FILE_TMP, "w") as cache:
                for (host, user_map) in host_map.items():
                    for (user, password) in user_map.items():
                        cache.write("{0} {1} {2}\n".format(host, user, base64.encodestring(password).strip()))
                cache.flush()
            # copy file after saved ok
            shutil.copyfile(LoginInfo.CACHE_FILE_TMP, LoginInfo.CACHE_FILE)
            os.remove(LoginInfo.CACHE_FILE_TMP)

        except:
            self.__process_exception()

    def show_hosts(self):
        self.host_map = {}
        try:
            with open(LoginInfo.CACHE_FILE, "r") as cache:
                # load login info
                self.__parse(cache.readlines())
        except:
            self.__process_exception()
        if self.host_map:
            print "Following hosts can be fast login:\033[32m"
            print "\n".join(self.host_map.keys())
            print "\033[0m"


class FastLogin:
    def __init__(self, option_values):
        self.password_suffix = None
        self.show_info = False
        self.show_white_list = False
        self.show_help = False

        if not option_values:
            return
        if "-s" in option_values:
            self.password_suffix = option_values["-s"]
            if not self.password_suffix:
                print "Password suffix not provided."
                exit(1)
        elif "-h" in option_values:
            self.show_help = True
        elif "-i" in option_values:
            self.show_info = True
        elif "-w" in option_values:
            self.show_white_list = True

    def execute(self, host, user, password):
        login_info = LoginInfo()

        # show all hosts
        if not host:
            login_info.show_hosts()
            return

        # search password
        (host, user, password) = login_info.search(host, user, password)
        password = password if not self.password_suffix else password + self.password_suffix

        # ssh login
        code = os.system("expect ssh-expect {0} {1} {2} 2>/dev/null".format(host, user, password))
        if code == 0:
            if login_info.password_changed:
                print "Password updated."
            login_info.save()
        else:
            login_info.try_remove(host, user, password)
            if os.system("which pbcopy > /dev/null") == 0:
                commands.getstatusoutput("bash -c 'echo -n x {} {} {}' | pbcopy".format(host, user, password))
                print "Fast Login failed, login info has been copied, use Ctrl + V to try again."


if __name__ == '__main__':
    (option, value, host, user, password) = (None, None, None, None, None)

    # retrieve option
    option_values = {}
    login_args = []
    index = 1
    length = len(sys.argv)
    while index < length:
        arg = sys.argv[index]
        if arg.startswith("-"):
            option = arg
            if index + 1 < length:
                value = sys.argv[index + 1]
            option_values[option] = value
            index += 2
        else:
            login_args.append(arg)
            index += 1

    # process login info
    length = len(login_args)
    if length >= 1:
        host = login_args[0]
    if length >= 2:
        user = login_args[1]
    if length >= 3:
        password = login_args[2]

    # run command
    fast_login = FastLogin(option_values)
    if fast_login.show_help:
        print "FastLogin:\n" \
              "\tx host [user] [password] [option [value]]\n" \
              "options:\n" \
              "\t-s suffix\t\tAppend dynamic suffix to password\n" \
              "\t-i\t\t\tShow recorded login info\n" \
              "\t-w\t\t\tShow white list config\n" \
              "\t-h\t\t\tShow this help message\n"
    elif fast_login.show_info:
        os.system("cat {}".format(LoginInfo.CACHE_FILE))
    elif fast_login.show_white_list:
        os.system("cat {}".format(WhiteList.WHITE_LIST_CONFIG))
    else:
        fast_login.execute(host, user, password)
