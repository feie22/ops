#!/bin/usr/python
#coding: utf-8
#===============================================================================
#         FILE: HbaseExpansion.py
#  DESCRIPTION: Hbase扩容包安装
#       AUTHOR: anbaoyong/wangdelong5
#      VERSION: 1.1
#      CREATED: 2015-12-02
#       UPDATE: 2016-8-15
#===============================================================================
import os
import commands
# import urllib2
# import random
import sys
# import stat
#public
conf_dir = '/software/servers/'
ret = {"result":"NONE","details":"NONE"}
bak_dir='/software/servers/softwarebak'
res = ''
# url=['http://172.19.154.14:8485/salt-git','http://172.19.154.13:8485/salt-git']

##hbase
bashrc_file = "/home/hadp/.bashrc"
if not os.path.exists(bashrc_file):
    sys.exit("bashrc文件不存在")
cmd_jdk = "awk -F '/' '/\/software\/servers\/jdk/{print $NF}' %s" % bashrc_file
cmd_hadoop = "awk -F '/' '/\/software\/servers\/hadoop/{print $NF}' %s" % bashrc_file
cmd_hbase = "awk -F '/' '/\/software\/servers\/hbase/{print $NF}' %s" % bashrc_file
(s1, jdk_v) = commands.getstatusoutput(cmd_jdk)
(s2, hadoop_v) = commands.getstatusoutput(cmd_hadoop)
(s3, hbase_v) = commands.getstatusoutput(cmd_hbase)
hbase_user = 'hadp'
hbase_group = 'hadp'
# hbase_data_dir = ['/data0/zookeeper-3.4.5/logs']
# hbase_zk_list = ['zookeeper-3.4.5.tar.gz', jdk_v + '.tar.gz']
hbase_tar_list = [jdk_v + '.tar.gz', hbase_v + '.tar.gz']
# hbase_hadoop_list = ['hadoop-2.6.0.tgz']
hbase_hadoop_list = [hadoop_v + '.tar.gz']

## Modify Hadoop & Hbase deploy version
#hbase_tar_list = ['jdk-7u67-linux-x64.tar.gz','hbase-0.94.18-security.tar.gz']
#hbase_hadoop_list = ['hadoop-2.2.0.tar.gz']


class Install():
    def __init__(self):
        pass

    def cmd(self,arg):
        (status, output) = commands.getstatusoutput(arg)
        global res
        if status:
            res = 'False:%s%s:::%s' % (arg,output,res)
            return False
        else:
            res = 'True:%s%s:::%s' % (arg,output,res)
            return True

    def deploy(self,pkg_list,target_path):
        for pkg in pkg_list:
            if pkg == 'jdk1.6.0_25.tar.gz' or pkg == 'jdk1.7.0_67.tar.gz':
                if os.path.exists('/software/servers/jdk1.6.0_25') and os.path.exists('/software/servers/jdk1.7.0_67'):
                    continue
            pkg_path = bak_dir + os.sep + pkg
            if os.path.exists(pkg_path):
                os.chdir(bak_dir)
                if not self.cmd('tar xf %s -C %s' % (pkg,target_path)):
                    return False,res
            else:
                info = 'pkg %s is not exists !' % pkg
                return False,info
        return True,res

    def returninfo(self,bool,info):
        ret['result'] = bool
        ret['details'] = info
        return ret

install=Install()


def hbase_hadoop():
    global res
    pkginstall = install.deploy(hbase_hadoop_list,conf_dir)
    if not pkginstall[0]:
        return install.returninfo(False,pkginstall[1])
    else:
        install.cmd('chown -R %s:%s /software' % (hbase_user,hbase_group))
        install.cmd('chown -R %s:%s /data*/' % (hbase_user,hbase_group))
        return install.returninfo(True,res)

def hbase():
    global res
    pkginstall = install.deploy(hbase_tar_list,conf_dir)
    if not pkginstall[0]:
        return install.returninfo(False,pkginstall[1])
    else:
        # for dir in hbase_data_dir:
        #     os.system('mkdir -p %s' % dir)
        install.cmd('chown -R %s:%s /software' % (hbase_user,hbase_group))
        install.cmd('chown -R %s:%s /data0/' % (hbase_user,hbase_group))
        return install.returninfo(True,res)
