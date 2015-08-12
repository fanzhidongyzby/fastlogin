#!/usr/bin/python
# encoding: UTF-8

import sys
import re
import commands
import os
import subprocess

# get args
ip = "127.0.0.1"
user = "ambari"
password = "ambari"

argc = len(sys.argv)
if argc <= 1:
    print "no ip argument !"
    sys.exit(1)
ip = sys.argv[1]

if argc >= 3:
    user = sys.argv[2]
    password = user

if argc >=4:
    password = sys.argv[3]


# valid ip
pt_ip4 = re.compile(r'^\d{1,3}$')
pt_ip34 = re.compile(r'^\d{1,3}\.\d{1,3}$')
pt_ip234 = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}$')
pt_ip1234 = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

if pt_ip4.search(ip):
    ip = "10.151.135." + ip
elif pt_ip34.search(ip):
    ip = "10.151." + ip
elif pt_ip234.search(ip):
    ip = "10." + ip
elif pt_ip1234.search(ip):
    ip = ip
else:
    print "bad ip argument: except char found"
    sys.exit(1)

ips = ip.split(".")

def filter(x):
  x = int(x)
  if x < 0 or x > 255:
    print "bad ip argument: out of range 0 - 255"
    sys.exit(1)

map(filter, ips)

print ip, user, password

# gen exp
script = '''#!/usr/bin/expect

set host      "$HOST"
set user      "$USER"
set password  "$PASSWORD"
set timeout -1

spawn ssh ${user}@${host}
expect {
        "password" {send "${password}\r"}
        "*yes*" {send "yes\r"}
}

interact
'''

script = script.replace("$HOST", ip)
script = script.replace("$USER", user)
script = script.replace("$PASSWORD", password)

f = open("dossh.exp", "w")
print >> f, script

(ret, out) = commands.getstatusoutput("chmod +x dossh.exp")
if ret != 0:
  print "change file mode failed !"
  sys.exit(1)

