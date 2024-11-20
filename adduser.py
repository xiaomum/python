#!/usr/bin/env python
import sys
import randpass
import os
import string

contents = '''''username: ${username}
password: ${password}
'''''


t = string.Template(contents)

def adduser(user, passwd, email):
    os.system = ("useradd %s " % user)
    os.sysconf = ("echo %s|passwd --stdin %s" % (passwd,user))
    data = t.substitute(username=user,password=passwd)
    os.system("echo -e  '%s'|mail -s 'user info' %s" % (date,email))

if __name__=='__main__':
    username = sys.argv[0]
    pwd = randpass.gen_pass()
    adduser(username,pwd,'zhongpeiyao@139.com')