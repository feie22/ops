#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = '登陆远程服务器执行命令'
__author__ = 'Cruis'
__mtime__ = '2016/3/14 0014'

"""
# 导入模块
import pexpect
import commands

# 定义远程登陆及执行命令函数
def ssh_cmd(r_ip, passwd, cmd):
    ret = -1

    # 定义expect连接
    ssh = pexpect.spawn('ssh root@%s "%s"' % (r_ip, cmd))

    try:
        # 定义可能出现的状态值
        i = ssh.expect(['password:', 'continue connecting (yes/no)?'], timeout=5)

        if i == 0 :

            # 根据状态值发送密码
            ssh.sendline(passwd)
        elif i == 1:

            # 根据状态值发送字符及密码
            ssh.sendline('yes\n')
            ssh.expect('password: ')
            ssh.sendline(passwd)

        # 发送要执行的命令并打印
        ssh.sendline(cmd)
        r = ssh.read()
        print r
        ret = 0

    # expect结束异常捕获
    except pexpect.EOF:
        print "EOF"
        ssh.close()
        ret = -1

    # 超时异常捕获
    except pexpect.TIMEOUT:
        print "TIMEOUT"
        ssh.close()
        ret = -2

    return ret

if __name__ == '__main__':

    # 定义远程主机IP及密码
    r_ip = '192.168.0.110'
    passwd = '000000'

    # 定义获取本机IP的命令（这里取的是本机第一个网络接口的IP地址）
    get_ip_cmd = ''' ifconfig | awk '/inet addr/{print $2}'| head -1 | awk -F ":" '{print $2}' '''
    (s, localIP)= commands.getstatusoutput(get_ip_cmd)
    cmd = 'echo %s >> /tmp/remote_ip.txt' % localIP

    ssh_cmd(r_ip, passwd, cmd)
    ssh_cmd()



