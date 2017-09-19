import getpass
import re

from user_config import *
from logger import log
from message import Message

from white_list import white_list


# login record
class LoginRecord:
    def __init__(self, host, user, password=None, use_password_suffix=False, proxy_host=None, proxy_user=None):
        self.host = host
        self.user = user
        self.password = password
        self.use_password_suffix = not not use_password_suffix
        self.proxy_host = proxy_host
        self.proxy_user = proxy_user

    # copy new record
    def duplicate(self):
        record = None
        if LoginRecord.valid(self):
            record = LoginRecord(self.host, self.user, self.password,
                                 self.use_password_suffix,
                                 self.proxy_host, self.proxy_user)

        return record

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if not other:
            return False
        return self is other or \
               self.host == other.host \
               and self.user == other.user \
               and self.password == other.password

    def __cmp__(self, other):
        if not other:
            return 1
        if not self.host:
            return -1
        return self.host > other.host and 1 or -1

    def __str__(self):
        return Message.format("{}:{}{}@{}{}", self.user, self.password,
                              self.use_password_suffix and "<suffix>" or "",
                              self.host,
                              Message.format(" <- {}@{}", self.proxy_user, self.proxy_host)
                              if self.proxy_host and self.proxy_user else ""
                              )

    # print login record with color
    def color_string(self, show_password=False):
        return Message.format("\033[35m{}\033[0m" +
                              ":\033[33m{}\033[0m" +
                              "{}" +
                              "@\033[32m{}\033[0m" +
                              "{}",
                              self.user,
                              self.password if self.password and show_password else "<password>",
                              "\033[31m[suffix]\033[0m" if self.use_password_suffix else "",
                              self.host,
                              Message.format("\033[34m <- \033[0m\033[35m{}\033[0m@\033[32m{}\033[0m",
                                             self.proxy_user,
                                             self.proxy_host)
                              if self.proxy_host and self.proxy_user else ""
                              )

    @staticmethod
    def valid_host(host):
        if host and isinstance(host, str):
            return True
        else:
            log.debug("invalid condition in valid_host")

    @staticmethod
    def valid_user(user):
        if user and isinstance(user, str):
            return True
        else:
            log.debug("invalid condition in valid_user")

    @staticmethod
    def valid_password(password):
        if isinstance(password, str):
            return True
        else:
            log.debug("invalid condition in valid_password")

    @staticmethod
    def valid_suffix(use_password_suffix):
        if isinstance(use_password_suffix, bool):
            return True
        else:
            log.debug("invalid condition in valid_suffix")

    @staticmethod
    def valid_proxy(proxy_host, proxy_user):
        if (proxy_host == None and proxy_user == None) or \
                (isinstance(proxy_user, str) and isinstance(proxy_user, str)):
            return True
        else:
            log.debug("invalid condition in valid_proxy")

    @staticmethod
    def valid(record):
        return isinstance(record, LoginRecord) \
               and LoginRecord.valid_host(record.host) \
               and LoginRecord.valid_user(record.user) \
               and LoginRecord.valid_password(record.password) \
               and LoginRecord.valid_suffix(record.use_password_suffix) \
               and LoginRecord.valid_proxy(record.proxy_host, record.proxy_user)


# login info file
class LoginInfo:
    def __init__(self):
        # host -> user -> record
        self.host_map = {}
        host_map = user_config.read(user_config.login_info_file, dict)

        # proxy records
        records_with_proxy = []
        for (host, user_map) in host_map.items():
            # invalid host
            if not LoginRecord.valid_host(host):
                continue

            # valid host
            if host not in self.host_map:
                self.host_map[host] = {}

            for (user, record) in user_map.items():
                # invalid user
                if not LoginRecord.valid_user(user):
                    continue

                # invalid record
                if not LoginRecord.valid(record) or record.host != host or record.user != user:
                    continue

                if record.proxy_host and record.proxy_user:
                    # check proxy later
                    records_with_proxy.append(record)
                else:
                    self.host_map[host][user] = record

        # check proxy
        for record in records_with_proxy:
            proxy_host = record.proxy_host
            proxy_user = record.proxy_user
            # if self.contains(proxy_host, proxy_user):
            self.host_map[record.host][record.user] = record

        # filter empty host
        host_map = {}
        for (host, user_map) in self.host_map.items():
            if len(user_map):
                host_map[host] = self.host_map[host]
        self.host_map = host_map

    def save(self):
        if user_config.write(user_config.login_info_file, self.host_map):
            log.debug("login info updated")
        else:
            log.debug("login info update failed")

    def __str__(self):
        return self.color_string(True)

    # print login info with color
    def color_string(self, show_password=False):
        records = []
        for (host, user_map) in self.host_map.items():
            for (user, record) in user_map.items():
                records.append(record)
        records.sort()
        return "\n".join(map(lambda r: r.color_string(show_password), records))

    # get all login hosts
    def get_hosts(self):
        hosts = self.host_map.keys()
        hosts.sort()
        return hosts

    # check host user record exists
    def contains(self, host, user):
        return host in self.host_map and user in self.host_map[host]

    # add login record, update if needed. proxy must be added first
    def add(self, record):
        if not LoginRecord.valid(record):
            return

        # check proxy if exists
        if record.proxy_host and record.proxy_user:
            if not self.contains(record.proxy_host, record.proxy_user):
                log.debug("proxy {}@{} not exist", record.proxy_user, record.proxy_host)
                return

        # add record
        if record.host not in self.host_map:
            self.host_map[record.host] = {}
        if record.user not in self.host_map[record.host]:
            self.host_map[record.host][record.user] = record
        else:
            last_record = self.host_map[record.host][record.user]
            if last_record != record:
                self.host_map[record.host][record.user] = record
                log.debug("record updated: {}", record)

    def valid_string(self, value):
        if isinstance(value, str) and value:
            control_chars = ''.join(map(unichr, range(0, 32) + range(127, 160)))
            control_char_re = re.compile('[%s]' % re.escape(control_chars))
            return not control_char_re.match(value)
        else:
            return False

    # force read one string
    def force_read(self, name, is_password=False):
        if not name or not isinstance(name, str):
            log.debug("invalid name")
            return None

        name = name[:1].upper() + name[1:]

        while (True):
            try:
                prompt = Message.format("{} must be provided: ", name)
                if is_password:
                    key = getpass.getpass(prompt)
                else:
                    key = str(raw_input(prompt).strip())
                if self.valid_string(key):
                    return key
            except KeyboardInterrupt:
                log.exception("\nNo {} was input", name)
                break
            except:
                log.exception()

    # choose one element from a list
    def __interactive_choose(self, key, elems, elem_name, elems_name=None, force_match=True):
        canceled = False
        if not elem_name:
            log.debug("invalid elem name")
            return None, canceled

        if not elems_name:
            elems_name = elem_name + "s"

        if not isinstance(elems, list) or len(elems) and not isinstance(elems[0], str):
            log.debug("invalid {} list type", elem_name)
            return key, canceled

        if not elems:
            if not key:
                log.debug("invalid {} key", elem_name)
            return key, canceled
        else:
            if not key:
                if force_match:
                    log.debug("invalid {} key", elem_name)
                    return None, canceled
            else:
                # match elem
                elems = filter(
                    lambda h: h.find(key) != -1 if key else False,
                    elems
                )

        chose_elem = None

        if elems and len(elems) > 1:
            log.info("Following {} were found:", elems_name)
            for index, item in enumerate(elems):
                log.tips("\t ({}): {}", index + 1, item)

            while (True):
                try:
                    number = int(raw_input("Choose one to continue: ").strip())
                    if 1 <= number <= len(elems):
                        chose_elem = elems[number - 1]
                    else:
                        log.debug("input num is out of index of matched {}", elems_name)
                except KeyboardInterrupt:
                    log.exception("\nNo {} was chose", elem_name)
                    canceled = True
                    break
                except:
                    log.exception()
                if chose_elem:
                    break
        else:
            chose_elem = elems[0] if elems else key
        return chose_elem, canceled

    # search match login record
    def search(self, host_key=None, user_key=None):
        record = None

        # choose host
        chose_host, canceled = self.__interactive_choose(host_key, self.host_map.keys(), "host")
        chose_host = self.force_read("host") if not chose_host and not canceled else chose_host
        if not chose_host:
            return record
        else:
            log.tips("Host's name: {}", chose_host)

        # choose user
        chose_user = user_key
        canceled = False
        if chose_host in self.host_map:
            chose_user, canceled = self.__interactive_choose(user_key,
                                                             self.host_map[chose_host].keys(), "user",
                                                             force_match=False)
        chose_user = self.force_read("user") if not chose_user and not canceled else chose_user
        if not chose_user:
            return record
        else:
            log.tips("User's name: {}", chose_user)

        # return record
        if chose_host in self.host_map and chose_user in self.host_map[chose_host]:
            # copy record
            record = self.host_map[chose_host][chose_user].duplicate()
        else:
            # new record
            return LoginRecord(chose_host, chose_user)
        return record

    # remove one record
    def remove(self, record):
        if not LoginRecord.valid(record):
            return

        # ignore white list
        if record.host in white_list:
            return

        # find and remove
        if record.host in self.host_map:
            if record.user in self.host_map[record.host]:
                last_record = self.host_map[record.host][record.user]
                if last_record == record:
                    if len(self.host_map[record.host]) == 1:
                        # only one record, remove host
                        del self.host_map[record.host]
                    else:
                        # only remove the user item
                        del self.host_map[record.host][record.user]

    # remove host or user
    def remove_host_or_user(self, host, user):
        if not host:
            return False
        if host in white_list:
            log.error("Host '{}' in white list, can not remove", host)
            return False
        # find and remove
        if host in self.host_map:
            if not user:
                # remove host
                del self.host_map[host]
            elif user in self.host_map[host]:
                if len(self.host_map[host]) == 1:
                    # only one record, remove host
                    del self.host_map[host]
                else:
                    # only remove the user item
                    del self.host_map[host][user]
        return True

    # clear
    def clear(self):
        self.host_map.clear()


login_info = LoginInfo()
