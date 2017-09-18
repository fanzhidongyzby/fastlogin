# FastLogin
ssh快速登录工具，免去记忆、输入机器、用户名和密码的烦恼。无论是直接登录，还是通过**跳板机**间接登录，都可以做到一键登录自动完成！

后台开发或者运营人员经常需要ssh登录大量的服务器，记下那么多枯燥的主机名和用户名、密码实在头疼，即便是用登录工具(XShell, SecureCRT, Putty)自带的记录主机的功能也不甚方便。FastLogin通过一个简单的脚本，帮助你快速关键字检索要登录的机器，并能自动填充用户名和密码。

其基本宗旨是：**用最少的击键次数实现SSH登录**

## 安装步骤

```bash
(florian) ~ $ git clone https://github.com/fanzhidongyzby/fastlogin.git
(florian) ~/fastlogin $ cd fastlogin
(florian) ~/fastlogin $ ./install /usr/local
```

## 功能测试

```bash
(florian) ~ $ x -h
FastLogin:
	x host [user] [password] [option [value]*]
options:
	-p <host> [<user>]	Specify proxy host and user
	-s <suffix>		Password suffix (proxy use first)
	-i			Show detail login info
	-i- <host> [<user>]	Remove host or user info
	-I			Show detail login info (see password)
	-w			Show white list config
	-w+ <host>		Add white list record
	-w- <host>		Remove white list record
	-D			Turn debug on
	-h			Show this help message
	-v			Show version

```
| 选项 |    参数     |                             含义                              |
| ---- | ----------- | ------------------------------------------------------------- |
| -p   | host [user] | 跳板机信息，自动从登录信息中检索                              |
| -s   | suffix      | 在登录密码后添加后缀登录 ，使用-p选项时，为跳板机密码添加后缀 |
| -i   |             | 显示保存的登录信息                                            |
| -i-  | host [user] | 删除主机或用户登录信息                                        |
| -I   |             | 显示保存的登录信息（含密码敏感信息）                          |
| -w   |             | 显示白名单配置                                                |
| -w+  | host        | 添加白名单记录                                                |
| -w-  | host        | 删除白名单记录                                                |
| -D   |             | 调试选项                                                      |
| -h   |             | 显示帮助                                                      |
| -v   |             | 显示版本信息                                                  |

## 卸载

```bash
(florian) ~ $ cd fastlogin
(florian) ~/fastlogin $ ./uninstall /usr/local
```

## 功能介绍

### 1. 登录记忆

FastLogin会自动记录成功登录过的机器名和用户密码。
1. 同一机器使用不同账户登录成功后仍能记录新的账户信息。
2. 同一机器使用相同帐户，但是不同密码登录成功后会自动更新密码信息。

```bash
(florian) ~ $ x arch admin admin
Host's name: arch
User's name: admin
Last login: Wed Dec 21 17:30:32 2016 from 10.211.55.2
[admin@arch ~]$ logout
Shared connection to arch closed.
(florian) ~ $ x
Following hosts can be fast login:
arch
```

### 2. 快捷登陆

FastLogin会自动匹配机器名，并根据历史登录信息登录对应机器。

```bash
(florian) ~ $ x a
Host's name: arch
User's name: admin
Last login: Wed Dec 21 17:30:39 2016 from 10.211.55.2
[admin@arch ~]$
```

### 3. 多项选择

FastLogin会在匹配到多个机器或可用的登录账户时，给用户提供了快捷选择。为避免多项选择，可适当调整主机/用户名关键字。

```bash
(florian) ~ $ x 1
Following hosts were found:
	 (1): 10.211.55.4
	 (2): 10.211.55.5
Choose one to continue: 1
Host's name: 10.211.55.4
Following users were found:
	 (1): admin
	 (2): test
Choose one to continue: 1
User's name: admin
Last login: Wed Dec 21 17:31:13 2016 from 10.211.55.2
[admin@arch ~]$
```

### 4. 跳板机登录支持

FastLogin可以实现跨机器登录，这在使用跳板机登录场景中十分有用。

```bash
(florian) ~ $ x centos admin admin -p arch admin
Host's name: centos
User's name: admin
Host's name: arch
User's name: admin
Warning: Permanently added 'centos' (ECDSA) to the list of known hosts.
admin@centos's password:
Last login: Wed Dec 21 04:14:07 2016 from 10.211.55.4
[admin@localhost ~]$
```

FastLogin会记录下来当前机器通过哪个跳板机登录成功过：

```bash
(florian) ~ $ x -I
Detail login records:
admin:admin@arch
admin:admin@centos <- admin@arch
```

因此之后再登录时，不需要重复输入跳板机信息：

```bash
(florian) ~ $ x e
Host's name: centos
User's name: admin
Host's name: arch
User's name: admin
Warning: Permanently added 'centos' (ECDSA) to the list of known hosts.
admin@centos's password:
Last login: Wed Dec 21 04:14:38 2016 from 10.211.55.4
[admin@localhost ~]$
```

### 5. 动态密码支持

一般企业的跳板机登录时都会需要输入动态口令，FastLogin通过密码后缀支持。

```bash
(florian) ~ $ x 10.211.55.4 test te -s st
Host's name: 10.211.55.4
User's name: test
Last login: Wed Dec 21 17:45:36 2016 from 10.211.55.2
[test@arch ~]$ logout
Shared connection to 10.211.55.4 closed.
(florian) ~ $ x -I
Detail login records:
test:te[suffix]@10.211.55.4
(florian) ~ $ x 4 t -s te
Host's name: 10.211.55.4
User's name: test
Last login: Wed Dec 21 17:48:00 2016 from 10.211.55.2
[test@arch ~]$
```

FastLogin只保存了固定的密码部分，动态密码需要登录时用-s选项指定。

### 6. 登录状态保活

即便使用-s选项指定动态密码后缀，每次登录输入动态密码的过程仍是非常麻烦。还得再次感谢SSH的socket复用机制，FastLogin利用了此特性。
在登录成功后，会在~/.fastlogin/tmp下保存有效的SSH连接信息，默认72小时内不需要在此输入密码（包括动态密码），而快捷登录命令不会受此影响。

如果对时长不满意，可以自定义配置。假设FastLogin的安装目录为/usr/local/fastlogin，那么直接修改配置文件即可。

```python
# /usr/local/fastlogin/config.properties
debug=off
ssh.keep.alive=72h
auto.remove=true

```

如果希望保活时间无限长，那么将ssh.keep.alive设为yes即可。

### 7. 其他功能

前边的示例中，都把登录密码写在命令行中了，显然有潜在的安全风险。因此FastLogin提供了交互式的输入方式。

```bash
(florian) ~ $ x arch
Host's name: arch
User must be provided: admin
User's name: admin
Password must be provided:
Last login: Wed Dec 21 18:22:31 2016 from 10.211.55.2
[admin@arch ~]$
```

登录失败后会自动删除清除原有登录信息，白名单机制主要用于备忘关键主机信息。
另外，也可以通过设置config.properties的auto.remove=false禁止登录失败清除主机信息。

```bash
(florian) ~ $ x -w+ centos
White list record 'centos' added
(florian) ~ $ x -w
White list config:
centos
(florian) ~ $ x -i- centos
Host 'centos' in white list, can not remove
```

以上介绍了FastLogin主要的功能，如果你在使用过程中遇到问题，或者有更好的建议，欢迎和我联系。

```bash
(florian) ~ $ x -v
FastLogin V1.0.0 Author: Florian alibaba.inc
FastLogin is a SSH tool which can help you:
  1. Record login host, user and password.
  2. Fast pattern match to fill login info.
  3. Dynamic token support with password suffix.
  4. Proxy login support.
  5. White list support to avoid login info auto-removed.
  6. SSH channel reuse.

```
