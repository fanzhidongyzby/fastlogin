import sys
import os
import shutil
import traceback


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
            host_map[host][user] = password
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
                    break

    def save(self):
        host_map = self.host_map

        try:
            with open(LoginInfo.CACHE_FILE_TMP, "w") as cache:
                for (host, user_map) in host_map.items():
                    for (user, password) in user_map.items():
                        cache.write("{0} {1} {2}\n".format(host, user, password))
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
    def __init__(self):
        pass

    def execute(self, host, user, password):
        login_info = LoginInfo()
        if not host:
            login_info.show_hosts()
            return
        (host, user, password) = login_info.search(host, user, password)
        code = os.system("expect ssh-expect {0} {1} {2} 2>/dev/null".format(host, user, password))
        if code == 0:
            if login_info.password_changed:
                print "Password updated."
            login_info.save()
        else:
            login_info.try_remove(host, user, password)
            print "Fast Login failed."


if __name__ == '__main__':
    (host, user, password) = (None, None, None)
    length = len(sys.argv)
    if length >= 4:
        password = sys.argv[3]
    if length >= 3:
        user = sys.argv[2]
    if length >= 2:
        host = sys.argv[1]
    else:
        print '''FastLogin:\n\tx host [user] [password]\n'''
    FastLogin().execute(host, user, password)
