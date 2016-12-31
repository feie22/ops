#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = '登陆远程服务器执行命令'
__author__ = 'Cruis'
__mtime__ = '2016/3/15 0015'

"""

import paramiko
import commands

# 定义基础信息
username = 'root'
passwd = '000000'
hostIP = '192.168.170.128'
port = 22

# 定义获取IP命令(本机第一个IP)，及远程执行命令（将本机IP添加到远程主机的指定文件中）
get_ip_cmd = ''' ifconfig | awk '/inet addr/{print $2}'| head -1 | awk -F ":" '{print $2}' '''
(s, localIP)= commands.getstatusoutput(get_ip_cmd)
cmd = 'echo %s >> /tmp/remote_ip.txt' % localIP

# 定义paramiko执行日志
paramiko.util.log_to_file('syslogin.log')

# 定义远程登陆及执行命令函数
def ssh_cmd(username, passwd, hostIP, port, cmd):
    try:
        s = paramiko.SSHClient()                                    #创建ssh客户端对象
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())     #没有本地hostkey的策略

        s.connect(hostIP, port, username, passwd, timeout=5)        #创建ssh连接
        stdin, stdout, stderr = s.exec_command(cmd)                 #执行命令
        for s in stderr.readlines():                                #打印错误输出
            print s,
        s.close()                                                   #关闭连接
    except:                                                         #捕获异常
        print 'Error'

if __name__ == '__main__':

    ssh_cmd(username, passwd, hostIP, port, cmd)                    #执行函数

