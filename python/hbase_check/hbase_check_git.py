#!/usr/bin/env python
# encoding: utf-8

"""
@description: hbase集群巡检脚本
@author: wangdelong@jd.com
@createtime: 2016/4/19 0019
@updatetime:
"""

import os
import sys
import commands
import json
import urllib
import salt.client

GIT_DIR = '/root/git/hbase/'
CLIENT = salt.client.LocalClient()

if len(sys.argv) ==1:
    print "error:请输入一个集群名称参数"
    sys.exit()
CLUSTER_NAME = sys.argv[1]

if not os.path.exists('/tmp/%s' % CLUSTER_NAME):
    print "info:创建集群日志目录"
    os.system('mkdir /tmp/%s' %CLUSTER_NAME)

def get_ip(cluster_name):

    #根据集群名称，获取tag_id
    url_tag_api = "http://bdp.jd.com/ops/api/server/findAllTags.ajax?tagType=2&appKey=123456&erp=wangdelong5"
    page1 = urllib.urlopen(url_tag_api)
    data1 = json.load(page1)
    data_list1 = data1['data']['dataList']
    tag_id = ''
    for i in range(0, len(data_list1)):
        if data_list1[i]['name'] == cluster_name:
            tag_id = data_list1[i]['id']
    if not tag_id:
        print "error:请输入正确的hbase集群名称"
        sys.exit()
    # print "tag is %s" % tag_id

    #根据tag_id获取集群的ip地址列表
    url_ip_api = "http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=19,%s&appKey=123456&erp=wangdelong5" % tag_id
    page2 = urllib.urlopen(url_ip_api)
    data2 = json.load(page2)
    data_list2 = data2['data']['dataList']
    ip_list2 = []
    for i in range(0, len(data_list2)):
        ip_list2.append(data_list2[i]['ip'])
    if not ip_list2:
        print "error:没有获取到hbase集群的IP地址"
        sys.exit()

    return ip_list2

#执行文件一致性检查
def check_md5():
    print "info:开始检查所有节点的配置文件一致性"
    ip_list = get_ip(CLUSTER_NAME)
    md5_dic = {}
    conf_list = []
    os.system('cd %s && git pull &> /dev/null' % GIT_DIR)
    top = GIT_DIR + CLUSTER_NAME
    if not os.path.exists(top):
        print "error:集群配置在git中不存在"

        sys.exit()
    dir_num = len(top)

    for root, dirs, files in os.walk(top, topdown=True):
        for name in files:
            conf_list.append(os.path.join(root, name)[dir_num:])

    for i in conf_list:#将md5校验值加入字典
        (s, r)=commands.getstatusoutput("md5sum %s%s%s | awk '{print $1}'" % (GIT_DIR, CLUSTER_NAME, i))
        md5_dic[i] = r

    os.system('rm -f /tmp/%s/md5.log ; touch /tmp/%s/md5.log' % (CLUSTER_NAME, CLUSTER_NAME))

    for n in md5_dic.iterkeys():
        cmd = "md5sum " + n + " | awk '{print $1}' "
        ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
        for i in ip_list:
            if ret_dic.has_key(i):
                if ret_dic[i] != md5_dic[n]:
                    os.system("echo '%s  %s' >> /tmp/%s/md5.log" % (i, n, CLUSTER_NAME ))
                    # print "server is %s, server_md5 is %s, source_md5 is %s " % (i, ret_dic[i], md5_dic[n])
            else:
                os.system("echo '%s can not be connected!' >> /tmp/%s/md5.log" % (i, CLUSTER_NAME ))
    (s, r) = commands.getstatusoutput("cat /tmp/%s/md5.log | wc -l" % CLUSTER_NAME)
    if int(r):
        print "error:个别服务器配置文件不一致或个别服务器返回异常（/tmp/%s/md5.log）" % CLUSTER_NAME
    else:
        print "info:配置文件一致性检查正常"
        os.system('rm -rf /tmp/%s/md5.log' % CLUSTER_NAME)


def check_service():
    print "info:开始检查所有节点的基础服务状态（crond snmpd gmond sshd rsyslog sysstat）"
    ip_list = get_ip(CLUSTER_NAME)
    os.system('rm -f /tmp/%s/service.log ; touch /tmp/%s/service.log' % (CLUSTER_NAME, CLUSTER_NAME))
    cmd = "for i in crond snmpd gmond sshd rsyslog sysstat; do service $i status; done |grep -v pid | awk '{print $1}'"
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s  %s' >> /tmp/%s/service.log" % (i, ret_dic[i], CLUSTER_NAME))
        else:
            os.system("echo '%s can not be connected!' >> /tmp/%s/service.log" % (i, CLUSTER_NAME ))
    (s, r) = commands.getstatusoutput("cat /tmp/%s/service.log | wc -l" % CLUSTER_NAME)
    if int(r):
        print "error:个别基础服务未安装(未运行)或个别服务器返回异常（/tmp/%s/service.log）" % CLUSTER_NAME
    else:
        print "info:基础服务状态正常"
        os.system('rm -rf /tmp/%s/service.log' % CLUSTER_NAME)

#执行文件错误检查
def check_messages():
    print "info:开始检查所有节点系统日志messages文件"
    ip_list = get_ip(CLUSTER_NAME)
    os.system('rm -f /tmp/%s/message.log ; touch /tmp/%s/message.log' % (CLUSTER_NAME, CLUSTER_NAME))
    cmd = "cat /var/log/messages |egrep  'fail|error'"
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s----------\n%s' >> /tmp/%s/message.log" % (i, ret_dic[i], CLUSTER_NAME))
        else:
            os.system("echo '%s can not be connected!' >> /tmp/%s/message.log" % (i, CLUSTER_NAME ))
    (s, r) = commands.getstatusoutput("cat /tmp/%s/message.log | wc -l" % CLUSTER_NAME)
    if int(r):
        print "error:系统日志messages有报错信息或个别服务器返回异常（/tmp/%s/message.log）" % CLUSTER_NAME
    else:
        print "info:系统日志messages文件正常"
        os.system('rm -rf /tmp/%s/messages.log' % CLUSTER_NAME)

def check_dmesg():
    print "info:开始检查所有节点系统日志dmesg文件"
    ip_list = get_ip(CLUSTER_NAME)
    os.system('rm -f /tmp/%s/dmesg.log ; touch /tmp/%s/dmesg.log' % (CLUSTER_NAME, CLUSTER_NAME))
    cmd = 'dmesg |grep -E -i "error" |grep -v "failed with error -22"| grep -v "ERST: Error Record"| grep -v "ACPI Error:" '
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s----------\n%s' >> /tmp/%s/dmesg.log" % (i, ret_dic[i], CLUSTER_NAME))
        else:
            os.system("echo '%s can not be connected!' >> /tmp/%s/dmesg.log" % (i, CLUSTER_NAME ))
    (s, r) = commands.getstatusoutput("cat /tmp/%s/dmesg.log | wc -l" % CLUSTER_NAME)
    if int(r):
        print "error:系统日志dmesg有报错信息或个别服务器返回异常（/tmp/%s/dmesg.log）" % CLUSTER_NAME
    else:
        print "info:系统日志dmesg文件正常"
        os.system('rm -rf /tmp/%s/dmesg.log' % CLUSTER_NAME)
def check_loadavg():
    print "info:开始检查所有节点的平均负载"
    ip_list = get_ip(CLUSTER_NAME)
    
    os.system('rm -f /tmp/%s/load.log ; touch /tmp/%s/load.log' % (CLUSTER_NAME, CLUSTER_NAME))
    cmd = "awk '{if($1>50 && $2>50 && $3>50) print $1,$2,$3}' /proc/loadavg"
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s load is [%s]' >> /tmp/%s/load.log" % (i, ret_dic[i], CLUSTER_NAME))
        else:
            os.system("echo '%s can not be connected!' >> /tmp/%s/load.log" % (i, CLUSTER_NAME ))
    (s, r) = commands.getstatusoutput("cat /tmp/%s/load.log | wc -l" % CLUSTER_NAME)
    if int(r):
        print "error:个别服务器平均负载异常或个别服务器返回异常（/tmp/%s/load.log）" % CLUSTER_NAME
    else:
        print "info:所有节点负载正常"
        os.system('rm -rf /tmp/%s/load.log' % CLUSTER_NAME)

def check_disk_use():
    print "info:开始检查所有节点的磁盘使用率"
    ip_list = get_ip(CLUSTER_NAME)
    os.system('rm -f /tmp/%s/disk.log ; touch /tmp/%s/disk.log' % (CLUSTER_NAME, CLUSTER_NAME))
    cmd = '''df -h|grep -E 'data*|/'|awk '{print "dir:"$6 " used:"$5}'|grep -E '([9][5-9]|100)%' '''
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s----------\n%s' >> /tmp/%s/disk.log" % (i, ret_dic[i], CLUSTER_NAME))
        else:
            os.system("echo '%s can not be connected!' >> /tmp/%s/disk.log" % (i, CLUSTER_NAME ))
    (s, r) = commands.getstatusoutput("cat /tmp/%s/disk.log | wc -l" % CLUSTER_NAME)
    if int(r):
        print "error:个别服务器磁盘使用率异常或个别服务器返回异常（/tmp/%s/disk.log）" % CLUSTER_NAME
    else:
        print "info:所有节点磁盘使用率正常"
        os.system('rm -rf /tmp/%s/disk.log' % CLUSTER_NAME)

def check_inode_use():
    print "info:开始检查所有节点的磁盘inode使用率"
    ip_list = get_ip(CLUSTER_NAME)
    os.system('rm -f /tmp/%s/inode.log ; touch /tmp/%s/inode.log' % (CLUSTER_NAME, CLUSTER_NAME))
    cmd = '''df -i|grep -E 'data*|/' |awk '{print "dir:"$6 " tused:"$5}'|grep -E '([7-9][0-9]|100)%' '''
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s----------\n%s' >> /tmp/%s/inode.log" % (i, ret_dic[i], CLUSTER_NAME))
        else:
            os.system("echo '%s can not be connected!' >> /tmp/%s/inode.log" % (i, CLUSTER_NAME ))
    (s, r) = commands.getstatusoutput("cat /tmp/%s/inode.log | wc -l" % CLUSTER_NAME)
    if int(r):
        print "error:个别服务器磁盘inode使用率异常或个别服务器返回异常（/tmp/%s/inode.log）" % CLUSTER_NAME
    else:
        print "info:所有节点磁盘inode使用率正常"
        os.system('rm -rf /tmp/%s/inode.log' % CLUSTER_NAME)


def check_mem_use():
    print "info:开始检查所有节点的内存使用率"
    ip_list = get_ip(CLUSTER_NAME)
    os.system('rm -f /tmp/%s/mem.log ; touch /tmp/%s/mem.log' % (CLUSTER_NAME, CLUSTER_NAME))
    cmd = '''free -m|grep "Mem"|awk '{if(($3-$7-$6)/$2 > 0.9) print ($3-$7-$6)/$2}' '''
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s memory usage is %s' >> /tmp/%s/mem.log" % (i, ret_dic[i], CLUSTER_NAME))
        else:
            os.system("echo '%s can not be connected!' >> /tmp/%s/mem.log" % (i, CLUSTER_NAME ))
    (s, r) = commands.getstatusoutput("cat /tmp/%s/mem.log | wc -l" % CLUSTER_NAME)
    if int(r):
        print "error:个别服务器内存使用率异常或个别服务器返回异常（/tmp/%s/mem.log）" % CLUSTER_NAME
    else:
        print "info:所有节点内存使用率正常"
        os.system('rm -rf /tmp/%s/mem.log' % CLUSTER_NAME)

def check_swap_use():
    print "info:开始检查所有节点的swap使用率"
    ip_list = get_ip(CLUSTER_NAME)
    os.system('rm -f /tmp/%s/swap.log ; touch /tmp/%s/swap.log' % (CLUSTER_NAME, CLUSTER_NAME))
    cmd = '''free -m|grep "Swap"|awk '{if($3/$2 > 0.2) print $3/$2}' '''
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s swap usage is %s' >> /tmp/%s/swap.log" % (i, ret_dic[i], CLUSTER_NAME))
        else:
            os.system("echo '%s can not be connected!' >> /tmp/%s/swap.log" % (i, CLUSTER_NAME ))
    (s, r) = commands.getstatusoutput("cat /tmp/%s/swap.log | wc -l" % CLUSTER_NAME)
    if int(r):
        print "error:个别服务器swap使用率异常或个别服务器返回异常（/tmp/%s/swap.log）" % CLUSTER_NAME
    else:
        print "info:所有节点swap使用率正常"
        os.system('rm -rf /tmp/%s/swap.log' % CLUSTER_NAME)

def check_bandwidth():
    print "info:开始检查所有节点的网卡带宽制式"
    ip_list = get_ip(CLUSTER_NAME)
    os.system('rm -f /tmp/%s/bandwidth.log ; touch /tmp/%s/bandwidth.log' % (CLUSTER_NAME, CLUSTER_NAME))
    for i in ip_list:
        cmd = "ethtool `ifconfig |grep %s -B 1 |head -1|awk '{print $1} '`|grep Speed|awk -F ':' '{print $2}'|awk -F 'M' '{if ($1 < 1000) print $1}'" % i
        ret_dic = CLIENT.cmd(i, 'cmd.run', [cmd])
        if ret_dic:
            if ret_dic[i]:
                os.system("echo '%s bandwidth is %sM' >> /tmp/%s/bandwidth.log" % (i, ret_dic[i], CLUSTER_NAME))
        else:
            os.system("echo '%s can not be connected!' >> /tmp/%s/bandwidth.log" % (i, CLUSTER_NAME ))
    (s, r) = commands.getstatusoutput("cat /tmp/%s/bandwidth.log | wc -l" % CLUSTER_NAME)
    if int(r):
        print "error:个别服务器网卡带宽制式异常或个别服务器返回异常（/tmp/%s/bandwidth.log）" % CLUSTER_NAME
    else:
        print "info:所有节点网卡制式正常"
        os.system('rm -rf /tmp/%s/bandwidth.log' % CLUSTER_NAME)

def check_connect():
    print "info:开始检查所有节点的连接数"
    ip_list = get_ip(CLUSTER_NAME)
    os.system('rm -f /tmp/%s/netstat.log ; touch /tmp/%s/netstat.log' % (CLUSTER_NAME, CLUSTER_NAME))
    cmd = "netstat -ant|wc -l|awk '{if($1 > 30000) print $1}' "
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s connections are %s' >> /tmp/%s/netstat.log" % (i, ret_dic[i], CLUSTER_NAME))
        else:
            os.system("echo '%s can not be connected!' >> /tmp/%s/netstat.log" % (i, CLUSTER_NAME))
    (s, r) = commands.getstatusoutput("cat /tmp/%s/netstat.log | wc -l" % CLUSTER_NAME)
    if int(r):
        print "error:个别服务器连接数超过3w异常或返回异常（/tmp/%s/netstat.log）" % CLUSTER_NAME
    else:
        print "info:所有节点连接数正常"
        os.system('rm -rf /tmp/%s/netstat.log' % CLUSTER_NAME)

def check_zombie():
    print "info:开始检查所有节点的僵尸进程"
    ip_list = get_ip(CLUSTER_NAME)
    os.system('rm -f /tmp/%s/zombie.log ; touch /tmp/%s/zombie.log' % (CLUSTER_NAME, CLUSTER_NAME))
    cmd = "ps -ef|grep defunct|grep -v grep"
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s zombie process is %s' >> /tmp/%s/zombie.log" % (i, ret_dic[i], CLUSTER_NAME))
        else:
            os.system("echo '%s can not be connected!' >> /tmp/%s/zombie.log" % (i, CLUSTER_NAME ))
    (s, r) = commands.getstatusoutput("cat /tmp/%s/zombie.log | wc -l" % CLUSTER_NAME)
    if int(r):
        print "error:个别服务器存在僵尸进程或返回异常（/tmp/%s/zombie.log）" % CLUSTER_NAME
    else:
        print "info:所有节点不存在僵尸进程"
        os.system('rm -rf /tmp/%s/zombie.log' % CLUSTER_NAME)

def check_bad_disk():
    print "info:开始检查所有节点磁盘状况"
    ip_list = get_ip(CLUSTER_NAME)
    os.system('rm -f /tmp/%s/bad_disk.log ; touch /tmp/%s/bad_disk.log' % (CLUSTER_NAME, CLUSTER_NAME))
    cmd = 'ls / | egrep "^data[0-9]"|xargs -i touch /{}/diskcheck ; ls / | egrep "^data[0-9]"|xargs -i rm /{}/diskcheck'
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list', username='hadp')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s has bad disk' >> /tmp/%s/bad_disk.log" % (i, CLUSTER_NAME ))
        else:
            os.system("echo '%s can not be connected!' >> /tmp/%s/bad_disk.log" % (i, CLUSTER_NAME ))
    (s, r) = commands.getstatusoutput("cat /tmp/%s/bad_disk.log | wc -l" % CLUSTER_NAME)
    if int(r):
        print "error:个别服务器存在坏盘或返回异常（/tmp/%s/bad_disk.log）" % CLUSTER_NAME
    else:
        print "info:所有节点不存在坏盘"
        os.system('rm -rf /tmp/%s/bad_disk.log' % CLUSTER_NAME)

    os.system('rm -f /tmp/%s/miss_disk.log ; touch /tmp/%s/miss_disk.log' % (CLUSTER_NAME, CLUSTER_NAME))
    cmd1 = 'grep data /etc/fstab|grep -v "#"|wc -l'
    cmd2 = 'df -h|grep data|wc -l'
    ret_dic1 = CLIENT.cmd(ip_list, 'cmd.run', [cmd1], expr_form='list')
    ret_dic2 = CLIENT.cmd(ip_list, 'cmd.run', [cmd2], expr_form='list')
    for i in ip_list:
        if ret_dic1.has_key(i):
            if ret_dic1[i] > ret_dic2[i]:
                os.system("echo '%s has missed disk' >> /tmp/%s/miss_disk.log" % (i, CLUSTER_NAME ))
        else:
            os.system("echo '%s can not be connected!' >> /tmp/%s/miss_disk.log" % (i, CLUSTER_NAME ))
    (s, r) = commands.getstatusoutput("cat /tmp/%s/miss_disk.log | wc -l" % CLUSTER_NAME)
    if int(r):
        print "error:个别服务器存在掉盘或返回异常（/tmp/%s/miss_disk.log）" % CLUSTER_NAME
    else:
        print "info:所有节点不存在掉盘"
        os.system('rm -rf /tmp/%s/bad_disk.log' % CLUSTER_NAME)



if __name__ == '__main__':

    print "开始检查---------------------------"
    check_md5()
    check_service()
    check_messages()
    check_dmesg()
    check_loadavg()
    check_disk_use()
    check_inode_use()
    check_mem_use()
    check_swap_use()
    check_bandwidth()
    check_connect()
    check_zombie()
    check_bad_disk()
    # ip_list = get_ip(CLUSTER_NAME)
    # print ip_list
    print "检查结束----------------------------"