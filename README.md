# FastLogin
ssh快速登录工具，免去记忆、输入机器、用户名和密码的烦恼。

后台开发或者运营人员经常需要ssh登录大量的服务器，记下那么多枯燥的主机名和用户名、密码实在头疼，即便是用登录工具(XShell, SecureCRT, Putty)自带的记录主机的功能也不甚方便。FastLogin通过一个简单的脚本，帮助你快速关键字检索要登录的机器，并能自动填充用户名和密码。

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
	x host [user] [password] [option [value]]
options:
	-s suffix		Append dynamic suffix to password
	-i			Show recorded login info
	-w			Show white list config
	-h			Show this help message

```
| 选项  |   参数   |               含义                |
| --- | ------ | ------------------------------- |
| -s  | suffix | 登录时，在保存的密码基础上添加后缀suffix ，如Token |
| -i  |        | 显示保存的登录信息 ~/.fastlogin.info     |
| -w  |        | 显示白名单配置 ~/.fastlogin.whitelist  |
| -h  |        | 显示帮助                            |

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
(florian) ~ $ x host1 user1 pass1
...
[user1@host1 /home/user1] $ exit
Connection to host1 closed.
(florian) ~ $ x
Following hosts can be fast login:
host1

```

### 2. 快捷登陆

FastLogin会自动匹配机器名，并根据历史登录信息登录对应机器。

```bash
(florian) ~/code/fastlogin $ x host
...
[user1@host1 /home/user1] $ exit
Connection to host1 closed.
(florian) ~/code/fastlogin $ x host user1
...
[user1@host1 /home/user1] $ exit
Connection to host1 closed.
```

### 3. 多项选择

FastLogin会在匹配到多个机器，或者同一个机器包含多个可用的登录账户时，给用户提供了快捷选择。

匹配到多个机器时(为避免多项选择，尽可能细化查找主机名关键字)：

```bash
(florian) ~ $ x host
Following hosts were found:
	 1: host2
	 2: host1
Choose one to continue:

```
匹配到多个账户时(为避免多项选择，可指定用户名)：

```bash
(florian) ~ $ x 2
Following users / password were found:
	 1: user2 / pass2
	 2: user3 / pass3
Choose one to continue:

```

### 4. 跳板机登录支持

使用-s选项可以实现跳板机登录支持，结合白名单机制可以防止未使用-s选项导致跳板机登录信息被清除。

```bash
(florian) ~ $ x -w
login-host
(florian) ~ $ x login-host user password -s token
...
[user1@login-host /home/user] $ exit
Connection to login-host closed.
(florian) ~ $ x login-host
...
Fast Login failed, login info has been copied, use Ctrl + V to try again.
```
