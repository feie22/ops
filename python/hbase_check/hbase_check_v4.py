#!/usr/bin/env python
# encoding: utf-8

"""
@description: hbase集群巡检脚本
@author: wangdelong
@createtime: 2016/4/19 0019
@updatetime: 2016/5/6
"""

import os
import sys
import time
import datetime
import commands
import json
import urllib
import salt.client
import MySQLdb

GIT_DIR = '/job/git/hbase/'
LOG_DIR = '/job/log/'
ERROR_LOG = '/job/log/ERROR.log'
NOW = datetime.datetime.now()
TIME_STRING = NOW.strftime("%Y-%m-%d %H:%M:%S")
CHECK_TIME = NOW.strftime("%Y-%m-%d#%H:%M")
CLIENT = salt.client.LocalClient()
os.system('cd %s && git pull &> /dev/null' % GIT_DIR)
NAME_LIST = os.listdir(GIT_DIR)
NAME_LIST.remove('.git')
NAME_LIST.remove('README.md')
LOG_VALUE = []
SUM_VALUE = []

def get_ip(cluster_name):

    # 根据集群名称，获取tag_id
    url_tag_api = "http://bdp.jd.com/ops/api/server/findAllTags.ajax?tagType=2&appKey=123456&erp=wangdelong5"
    time.sleep(0.01)
    page1 = urllib.urlopen(url_tag_api)
    data1 = json.load(page1)
    data_list1 = data1['data']['dataList']
    tag_id = ''
    for i in range(0, len(data_list1)):
        if data_list1[i]['name'] == cluster_name:
            tag_id = data_list1[i]['id']
    if not tag_id:
        # print "ERROR:请输入正确的hbase集群名称"
        sys.exit()
    # print "tag is %s" % tag_id

    # 根据tag_id获取集群的ip地址列表
    url_ip_api = "http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=19,%s&appKey=123456&erp=wangdelong5" % tag_id
    page2 = urllib.urlopen(url_ip_api)
    data2 = json.load(page2)
    data_list2 = data2['data']['dataList']
    ip_list2 = []
    for i in range(0, len(data_list2)):
        ip_list2.append(data_list2[i]['ip'])
    if not ip_list2:
        # print "ERROR:没有获取到hbase集群的IP地址"
        sys.exit()

    # 获取ZK节点IP地址
    url_ip_zk = "http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=19,10,%s&appKey=123456&erp=wangdelong5" % tag_id
    page3 = urllib.urlopen(url_ip_zk)
    data3 = json.load(page3)
    data_list3 = data3['data']['dataList']
    ip_list3 = []
    for i in range(0, len(data_list3)):
        ip_list3.append(data_list3[i]['ip'])

    # 去除ZK节点IP
    if ip_list3:
        ip_list = list(set(ip_list2).difference(set(ip_list3)))
    else:
        ip_list = ip_list2
    return ip_list

# 打印输出日志，记录数据库输入信息（LOG_VALUE）
def log_output(check_name, error, info):
    (s, r) = commands.getstatusoutput("cat %s/%s.log | wc -l" % (cluster_log_dir, check_name))
    if int(r):
        os.system('echo "%s: %s ERROR:%s（%s/%s.log）" >> %s ' % (cluster_name, CHECK_TIME, error, cluster_log_dir, check_name, check_log))
        os.system('echo "%s: %s ERROR:%s（%s/%s.log）" >> %s ' % (cluster_name, CHECK_TIME, error, cluster_log_dir, check_name, ERROR_LOG))
        ret_tuple = (TIME_STRING, cluster_name, check_name, 1,cluster_log_dir + '/' + check_name + '.log')
        LOG_VALUE.append(ret_tuple)
    else:
        os.system('echo "%s: %s INFO:%s" >> %s ' % (cluster_name, CHECK_TIME, info, check_log))
        os.system('rm -rf %s/%s.log' % (cluster_log_dir, check_name))
        ret_tuple = (TIME_STRING, cluster_name, check_name, 0,'')
        LOG_VALUE.append(ret_tuple)

#执行文件一致性检查
def check_md5():
    # print "INFO:开始检查文件一致性"
    os.system('echo "%s: %s INFO:开始检查所有节点的配置文件一致性" >> %s ' % (cluster_name, CHECK_TIME, check_log))
    # print "INFO:开始检查所有节点的配置文件一致性"
    # ip_list = get_ip(cluster_name)
    md5_dic = {}
    conf_list = []
    top = GIT_DIR + cluster_name
    if not os.path.exists(top):
        os.system('echo "%s: %s ERROR:集群配置在git中不存在" >> %s ' % (cluster_name, CHECK_TIME, ERROR_LOG))
        sys.exit()
    dir_num = len(top)

    for root, dirs, files in os.walk(top, topdown=True):
        for name in files:
            conf_list.append(os.path.join(root, name)[dir_num:])

    for i in conf_list:#将md5校验值加入字典
        (s, r)=commands.getstatusoutput("md5sum %s%s%s | awk '{print $1}'" % (GIT_DIR, cluster_name, i))
        md5_dic[i] = r

    os.system('rm -f %s/md5.log ; touch %s/md5.log' % (cluster_log_dir, cluster_log_dir))

    for n in md5_dic.iterkeys():
        cmd = "md5sum " + n + " | awk '{print $1}' "
        ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
        for i in ip_list:
            if ret_dic.has_key(i):
                if ret_dic[i] != md5_dic[n]:
                    os.system("echo '%s  %s' >> %s/md5.log" % (i, n, cluster_log_dir ))
                    # # print "server is %s, server_md5 is %s, source_md5 is %s " % (i, ret_dic[i], md5_dic[n])
            else:
                os.system("echo '%s can not be connected!' >> %s/md5.log" % (i, cluster_log_dir ))

    error = '个别服务器配置文件不一致或个别服务器返回异常'
    info = '集群内节点配置文件一致性检查正常'
    log_output('md5', error, info)

# 基础服务安装检查
def check_service():
    # print "INFO:开始检查所有节点的基础服务状态（crond snmpd gmond sshd rsyslog sysstat）"
    os.system('echo "%s: %s INFO:开始检查所有节点的基础服务状态（crond snmpd gmond sshd rsyslog sysstat）" >> %s ' % (
        cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/service.log ; touch %s/service.log' % (cluster_log_dir, cluster_log_dir))
    cmd = "for i in crond snmpd gmond sshd rsyslog sysstat; do service $i status; done |grep -v pid | awk '{print $1}'"
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s  %s' >> %s/service.log" % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s can not be connected!' >> %s/service.log" % (i, cluster_log_dir ))
    error = '个别基础服务未安装(未运行)或个别服务器返回异常'
    info = '集群内节点基础服务状态正常'
    log_output('service', error, info)

# 系统日志错误检查
def check_messages():
    # print "INFO:开始检查所有节点系统日志messages文件"
    os.system('echo "%s: %s INFO:开始检查所有节点系统日志messages文件" >> %s ' % (
        cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/message.log ; touch %s/message.log' % (cluster_log_dir, cluster_log_dir))
    cmd = '''cat /var/log/messages |egrep  "fail|error" | egrep -iv "ACPI Error" '''
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system('echo "%s----------\n%s" >> %s/message.log' % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s can not be connected!' >> %s/message.log" % (i, cluster_log_dir ))
    error = '系统日志messages有报错信息或个别服务器返回异常'
    info = '集群内节点系统日志messages文件正常'
    log_output('message', error, info)

# 系统dmesg错误检查
def check_dmesg():
    # print "INFO:开始检查所有节点系统日志dmesg文件"
    os.system('echo "%s: %s INFO:开始检查所有节点系统日志dmesg文件" >> %s ' % (
        cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/dmesg.log ; touch %s/dmesg.log' % (cluster_log_dir, cluster_log_dir))
    cmd = 'dmesg |egrep  -i "error" |egrep -iv "(failed with error -22)|(ERST: Error Record)|(ACPI ERROR)" '
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system('echo "%s----------\n%s" >> %s/dmesg.log' % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s can not be connected!' >> %s/dmesg.log" % (i, cluster_log_dir ))
    error = '系统日志dmesg有报错信息或个别服务器返回异常'
    info = '系统日志dmesg文件正常'
    log_output('dmesg', error, info)

# 系统负载检查
def check_loadavg():
    # print "INFO:开始检查所有节点的平均负载"
    os.system('echo "%s: %s INFO:开始检查所有节点的平均负载" >> %s ' % (
        cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/load.log ; touch %s/load.log' % (cluster_log_dir, cluster_log_dir))
    cmd = "awk '{if($1>50 && $2>50 && $3>50) print $1,$2,$3}' /proc/loadavg"
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s load is [%s]' >> %s/load.log" % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s can not be connected!' >> %s/load.log" % (i, cluster_log_dir ))
    error = '个别服务器平均负载异常或个别服务器返回异常'
    info = '所有节点负载正常'
    log_output('load', error, info)

# 磁盘空间使用率率检查
def check_disk_use():
    # print "INFO:开始检查所有节点的磁盘使用率"
    os.system('echo "%s: %s INFO:开始检查所有节点的磁盘使用率" >> %s ' % (
        cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/disk_use.log ; touch %s/disk_use.log' % (cluster_log_dir, cluster_log_dir))
    cmd = '''df -h|grep -E 'data*|/'|awk '{print "dir:"$6 " disk used:"$5}'|grep -E '([9][5-9]|100)%' '''
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s----------\n%s' >> %s/disk_use.log" % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s can not be connected!' >> %s/disk_use.log" % (i, cluster_log_dir ))
    error = '个别服务器磁盘使用率异常或个别服务器返回异常'
    info = '所有节点磁盘使用率正常'
    log_output('disk_use', error, info)

# 磁盘inode利用率检查
def check_inode_use():
    # print "INFO:开始检查所有节点的磁盘inode使用率"
    os.system('echo "%s: %s INFO:开始检查所有节点的磁盘inode使用率" >> %s ' % (
        cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/inode.log ; touch %s/inode.log' % (cluster_log_dir, cluster_log_dir))
    cmd = '''df -i|grep -E 'data*|/' |awk '{print "dir:"$6 " inode used:"$5}'|grep -E '([7-9][0-9]|100)%' '''
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s----------\n%s' >> %s/inode.log" % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s can not be connected!' >> %s/inode.log" % (i, cluster_log_dir ))
    error = '个别服务器磁盘inode使用率异常或个别服务器返回异常'
    info = '所有节点磁盘inode使用率正常'
    log_output('inode', error, info)

def check_mem_use():
    # print "INFO:开始检查所有节点的内存使用率"
    os.system('echo "%s: %s INFO:开始检查所有节点的内存使用率" >> %s ' % (
        cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/mem.log ; touch %s/mem.log' % (cluster_log_dir, cluster_log_dir))
    cmd = '''free -m|grep "Mem"|awk '{if(($3-$7-$6)/$2 > 0.9) print ($3-$7-$6)/$2}' '''
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s memory usage is %s' >> %s/mem.log" % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s can not be connected!' >> %s/mem.log" % (i, cluster_log_dir ))
    error = '个别服务器内存使用率异常或个别服务器返回异常'
    info = '所有节点内存使用率正常'
    log_output('mem', error, info)

def check_swap_use():
    # print "INFO:开始检查所有节点的swap使用率"
    os.system('echo "%s: %s INFO:开始检查所有节点的swap使用率" >> %s ' % (
        cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/swap.log ; touch %s/swap.log' % (cluster_log_dir, cluster_log_dir))
    cmd = '''free -m|grep "Swap"|awk '{if($3/$2 > 0.2) print $3/$2}' '''
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s swap usage is %s' >> %s/swap.log" % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s can not be connected!' >> %s/swap.log" % (i, cluster_log_dir ))
    error = '个别服务器swap使用率异常或个别服务器返回异常'
    info = '所有节点swap使用率正常'
    log_output('swap', error, info)

def check_bandwidth():
    # print "INFO:开始检查所有节点的网卡带宽制式"
    os.system('echo "%s: %s INFO:开始检查所有节点的网卡带宽制式" >> %s ' % (
        cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/bandwidth.log ; touch %s/bandwidth.log' % (cluster_log_dir, cluster_log_dir))
    for i in ip_list:
        cmd = "ethtool `ifconfig |grep %s -B 1 |head -1|awk '{print $1} '`|grep Speed|awk -F ':' '{print $2}'|awk -F 'M' '{if ($1 < 1000) print $1}'" % i
        ret_dic = CLIENT.cmd(i, 'cmd.run', [cmd])
        if ret_dic:
            if ret_dic[i]:
                os.system("echo '%s bandwidth is %sM' >> %s/bandwidth.log" % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s can not be connected!' >> %s/bandwidth.log" % (i, cluster_log_dir ))
    error = '个别服务器网卡带宽制式异常或个别服务器返回异常'
    info = '所有节点网卡制式正常'
    log_output('bandwidth', error, info)

def check_connect():
    # print "INFO:开始检查所有节点的连接数"
    os.system('echo "%s: %s INFO:开始检查所有节点的连接数" >> %s ' % (
        cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/netstat.log ; touch %s/netstat.log' % (cluster_log_dir, cluster_log_dir))
    cmd = "netstat -ant|wc -l|awk '{if($1 > 30000) print $1}' "
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s connections are %s' >> %s/netstat.log" % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s can not be connected!' >> %s/netstat.log" % (i, cluster_log_dir))
    error = '个别服务器连接数超过3w异常或返回异常'
    info = '所有节点连接数正常'
    log_output('netstat', error, info)

def check_zombie():
    # print "INFO:开始检查所有节点的僵尸进程"
    os.system('echo "%s: %s INFO:开始检查所有节点的僵尸进程" >> %s ' % (
        cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/zombie.log ; touch %s/zombie.log' % (cluster_log_dir, cluster_log_dir))
    cmd = "ps -ef|grep defunct|grep -v grep"
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s zombie process is %s' >> %s/zombie.log" % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s can not be connected!' >> %s/zombie.log" % (i, cluster_log_dir ))
    error = '个别服务器存在僵尸进程或返回异常'
    info = '所有节点不存在僵尸进程'
    log_output('zombie', error, info)

def check_bad_disk():
    # print "INFO:开始检查所有节点磁盘状况"
    os.system('echo "%s: %s IINFO:开始检查所有节点磁盘状况" >> %s ' % (
        cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/bad_disk.log ; touch %s/bad_disk.log' % (cluster_log_dir, cluster_log_dir))
    cmd = 'ls / | egrep "^data[0-9]"|xargs -i touch /{}/diskcheck ; ls / | egrep "^data[0-9]"|xargs -i rm /{}/diskcheck'
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list', username='hadp')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s has bad disk' >> %s/bad_disk.log" % (i, cluster_log_dir ))
        else:
            os.system("echo '%s can not be connected!' >> %s/bad_disk.log" % (i, cluster_log_dir ))
    error = '个别服务器存在坏盘或返回异常'
    info = '所有节点不存在坏盘'
    log_output('bad_disk', error, info)

    os.system('rm -f %s/miss_disk.log ; touch %s/miss_disk.log' % (cluster_log_dir, cluster_log_dir))
    cmd1 = 'grep data /etc/fstab|grep -v "#"|wc -l'
    cmd2 = 'df -h|grep data|wc -l'
    ret_dic1 = CLIENT.cmd(ip_list, 'cmd.run', [cmd1], expr_form='list')
    ret_dic2 = CLIENT.cmd(ip_list, 'cmd.run', [cmd2], expr_form='list')
    for i in ip_list:
        if ret_dic1.has_key(i):
            if ret_dic1[i] > ret_dic2[i]:
                os.system("echo '%s has missed disk' >> %s/miss_disk.log" % (i, cluster_log_dir ))
        else:
            os.system("echo '%s can not be connected!' >> %s/miss_disk.log" % (i, cluster_log_dir ))
    error = '个别服务器存在掉盘或返回异常'
    info = '所有节点不存在掉盘'
    log_output('miss_disk', error, info)

if __name__ == '__main__':

    for cluster_name in NAME_LIST:
        if not os.path.exists(LOG_DIR + cluster_name + '/' + CHECK_TIME):
            os.system('mkdir -p ' + LOG_DIR + cluster_name + '/' + CHECK_TIME)
        check_log = LOG_DIR + cluster_name + '/' + 'CHECK.log'
        os.system('echo "%s: %s 开始检查----------------------------" >> %s' % (cluster_name, CHECK_TIME, check_log))
        cluster_log_dir = LOG_DIR + cluster_name + '/' + CHECK_TIME
        ip_list = get_ip(cluster_name)
        # print "start " + cluster_name
        check_md5()
        check_service()
        check_loadavg()
        check_mem_use()
        check_disk_use()
        check_inode_use()
        check_bad_disk()
        check_swap_use()
        check_bandwidth()
        check_connect()
        check_zombie()
        check_messages()
        check_dmesg()
        # print "stop " + cluster_name
        os.system('echo "%s: %s 检查结束----------------------------" >> %s' % (cluster_name, CHECK_TIME, check_log))
        SUM_VALUE

    try:
        conn = MySQLdb.Connect(host='172.22.178.99', user='root', passwd='hadoop', db='ja_hbase',charset='utf8')
        cur=conn.cursor()
        cur.executemany('insert into hbase_check_log (start_time,cluster_name,check_itme,check_result,log_location) values(%s,%s,%s,%s,%s)',LOG_VALUE)
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        os.system('echo "Mysql Error %d: %s" >> %s ' % (e.args[0], e.args[1], ERROR_LOG))


    
