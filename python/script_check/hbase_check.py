#!/usr/bin/env python
# encoding: utf-8

"""
@description: hbase集群巡检脚本
@author: wangdelong
@createtime: 2016/4/19 0019
@updatetime: 2016/5/13
"""

import os
import sys
import time
import datetime
import commands
import json
import urllib
import httplib
import salt.client
import MySQLdb

def get_ip_offline(url):
    page = urllib.urlopen(url)
    data = json.load(page)
    data_list = data['data']['dataList']
    ip_list = []
    for i in range(0, len(data_list)):
        ip_list.append(data_list[i]['ip'])
    return ip_list

def get_ip_alive(cluster_name):

    # 根据集群名称，获取tag_id
    url_tag_api = "http://bdp.jd.com/ops/api/server/findAllTags.ajax?tagType=2&appKey=123456&erp=wangdelong5"
    time.sleep(0.05)
    page1 = urllib.urlopen(url_tag_api)
    data1 = json.load(page1)
    data_list1 = data1['data']['dataList']
    tag_id = ''
    for i in range(0, len(data_list1)):
        if data_list1[i]['name'] == cluster_name:
            tag_id = data_list1[i]['id']
    if not tag_id:
        print "ERROR:hbase集群名称错误:" + cluster_name
        # sys.exit()
        ip_list = []
        return ip_list, 0
    # print "tag is %s" % tag_id
    #获取监控状态id
    url_tag_jkzt = 'http://bdp.jd.com/ops/api/server/findAllTags.ajax?tagType=18&appKey=123456&erp=wangdelong5'
    page0 = urllib.urlopen(url_tag_jkzt)
    data0 = json.load(page0)
    data0_list = data0['data']['dataList']
    t_jkzt = []
    for m in range(0, len(data0_list)):
        t_jkzt.append(data0_list[m]['id'])
    ip_offline = []
    for t_id in t_jkzt:
        url_jkzt = 'http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=%s,%s&appKey=123456&erp=wangdelong5' % (tag_id, t_id)
        ip_offline.extend(get_ip_offline(url_jkzt))

    # 根据tag_id获取集群的(上线)ip地址列表
    url_ip_api = "http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=19,%s&appKey=123456&erp=wangdelong5" % tag_id
    time.sleep(0.1)
    page2 = urllib.urlopen(url_ip_api)
    data2 = json.load(page2)
    data_list_all = data2['data']['dataList']
    ip_list_all = []
    for i in range(0, len(data_list_all)):
        ip_list_all.append(data_list_all[i]['ip'])
    if not ip_list_all:
        os.system('echo "%s: %s 集群内无IP地址" >> %s' % (cluster_name, CHECK_TIME, ERROR_LOG))
        return None, None
    ip_list_all = list(set(ip_list_all).difference(set(ip_offline)))

    os.system('echo "%s: %s INFO:开始检查所有节点的存活状态" >> %s ' % (cluster_name, CHECK_TIME, check_log))
    os.system('rm -f %s/alive.log ; touch %s/alive.log' % (cluster_log_dir, cluster_log_dir))
    ret_dic = CLIENT.cmd(ip_list_all, 'test.ping', expr_form='list')
    ip_list_alive = ret_dic.keys()
    ip_no_alive = list(set(ip_list_all).difference(set(ip_list_alive)))
    if ip_no_alive:
        for i in ip_no_alive:
            os.system("echo '%s can not be connected' >> %s/alive.log" % (i, cluster_log_dir))
            os.system("echo '%s' >> %s/alive.log" % (i, LOG_DIR))
    error = '集群内个别服务器salt无法连通'
    info = '集群内节点存活状态正常'
    ret = log_output('alive', error, info)

    # 获取ZK节点IP地址
    url_ip_zk = "http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=19,10,%s&appKey=123456&erp=wangdelong5" % tag_id
    time.sleep(0.05)
    page3 = urllib.urlopen(url_ip_zk)
    data3 = json.load(page3)
    data_list3 = data3['data']['dataList']
    ip_list3 = []
    for i in range(0, len(data_list3)):
        ip_list3.append(data_list3[i]['ip'])

    # 去除ZK节点IP
    if ip_list3:
        ip_list = list(set(ip_list_alive).difference(set(ip_list3)))
    else:
        ip_list = ip_list_alive

    return ip_list, ret

# 打印输出日志，记录数据库输入信息（LOG_VALUE）
def log_output(check_name, error, info):
    (s, r) = commands.getstatusoutput("grep -E  '^172.' %s/%s.log| wc -l" % (cluster_log_dir, check_name))
    if int(r):
        os.system('echo "%s: %s ERROR:%s（%s/%s.log）" >> %s ' % (cluster_name, CHECK_TIME, error, cluster_log_dir, check_name, check_log))
        os.system('echo "%s: %s ERROR:%s（%s/%s.log）" >> %s ' % (cluster_name, CHECK_TIME, error, cluster_log_dir, check_name, ERROR_LOG))
        ret_tuple = (TIME_STRING, p_name, cluster_name, check_name, 1,cluster_log_dir + '/' + check_name + '.log')
    else:
        os.system('echo "%s: %s INFO:%s" >> %s ' % (cluster_name, CHECK_TIME, info, check_log))
        os.system('rm -rf %s/%s.log' % (cluster_log_dir, check_name))
        ret_tuple = (TIME_STRING, p_name, cluster_name, check_name, 0,'')
    LOG_VALUE.append(ret_tuple)
    return int(r)

# 上报phenix
def send_phenix(cluster_name, metricK, metricV, dt):
    params = {'monitorData' : json.dumps({'mr': 'ifspeed_monitor','tp': '004','t': TIMESTAMP ,'lc': {'s_1_k': '集群巡检结果' ,'s_1_n': '集群巡检结果'}, 'me':  [{'lc': {'s_1_k': cluster_name ,'s_1_n': cluster_name}, 'me':  [{'k': metricK,'v': metricV,'n': metricK,'dt': dt}]}]})}
    headerdata = {"Content-Type":"application/x-www-form-urlencoded", "Connection":"Keep-Alive"}
    server = httplib.HTTPConnection(URL)
    server.request("POST","/phenix/collector/monitorData.ajax",urllib.urlencode(params),headerdata)
    time.sleep(0.1)
    response = server.getresponse()
    # print cluster_name, response.status
    # print response.reason
    # print response.read()
    server.close()

# def check_alive():
#     os.system('echo "%s: %s INFO:开始检查所有节点的存活状态" >> %s ' % (cluster_name, CHECK_TIME, check_log))
#     os.system('rm -f %s/alive.log ; touch %s/alive.log' % (cluster_log_dir, cluster_log_dir))
#     for i in ip_list_all:
#         (s, r) = commands.getstatusoutput("ping -c 1 -w 1 %s $> /dev/null" % i)
#         if s:
#             os.system("echo '%s is not alive!' >> %s/alive.log" % (i, cluster_log_dir))
#     error = '集群内个别服务器无法ping通'
#     info = '集群内节点存活状态正常'
#     ret = log_output('alive', error, info)
#     return ret

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
        
    # print md5_dic

    os.system('rm -f %s/md5.log ; touch %s/md5.log' % (cluster_log_dir, cluster_log_dir))

    for n in md5_dic.iterkeys():
        cmd = "md5sum " + n + " | awk '{print $1}' "
        ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
        for i in ip_list:
            # (s, r) = commands.getstatusoutput("fping %s | awk '{print $3}'" % i)
            if ret_dic.has_key(i):
                if ret_dic[i] != md5_dic[n]:
                    os.system("echo '%s  %s' >> %s/md5.log" % (i, n, cluster_log_dir ))
                    # # print "server is %s, server_md5 is %s, source_md5 is %s " % (i, ret_dic[i], md5_dic[n])
            # elif r == 'alive':
            #     os.system("echo '%s does not install salt-minion!' >> %s/md5.log" % (i, cluster_log_dir))
            else:
                os.system("echo '%s salt-minon can not be connected!' >> %s/md5.log" % (i, cluster_log_dir ))

    error = '个别服务器配置文件不一致或个别服务器返回异常'
    info = '集群内节点配置文件一致性检查正常'
    ret = log_output('md5', error, info)
    return ret

# 基础服务安装检查
def check_service():
    # print "INFO:开始检查所有节点的基础服务状态（crond snmpd gmond sshd rsyslog sysstat）"
    os.system('echo "%s: %s INFO:开始检查所有节点的基础服务状态（crond snmpd gmond sshd rsyslog sysstat）" >> %s ' % (cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/service.log ; touch %s/service.log' % (cluster_log_dir, cluster_log_dir))
    cmd = "for i in crond snmpd gmond sshd rsyslog sysstat; do service $i status; done |grep -v pid | awk '{print $1}' || : "
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s  %s' >> %s/service.log" % (i, ret_dic[i], cluster_log_dir))
                os.system("echo '%s' >> %s/service.log" % (i, LOG_DIR))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/service.log" % (i, cluster_log_dir ))
    error = '个别基础服务未安装(未运行)或个别服务器返回异常'
    info = '集群内节点基础服务状态正常'
    ret = log_output('service', error, info)
    return ret

# 系统日志错误检查
def check_messages():
    # print "INFO:开始检查所有节点系统日志messages文件"
    os.system('echo "%s: %s INFO:开始检查所有节点系统日志messages文件" >> %s ' % (cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/message.log ; touch %s/message.log' % (cluster_log_dir, cluster_log_dir))
    cmd = '''cat /var/log/messages |egrep  "fail|error" | egrep -iv "ACPI Error" '''
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system('echo "%s----------\n%s" >> %s/message.log' % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/message.log" % (i, cluster_log_dir ))
    error = '系统日志messages有报错信息或个别服务器返回异常'
    info = '集群内节点系统日志messages文件正常'
    ret = log_output('message', error, info)
    return ret

# 系统dmesg错误检查
def check_dmesg():
    # print "INFO:开始检查所有节点系统日志dmesg文件"
    os.system('echo "%s: %s INFO:开始检查所有节点系统日志dmesg文件" >> %s ' % (cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/dmesg.log ; touch %s/dmesg.log' % (cluster_log_dir, cluster_log_dir))
    cmd = 'dmesg |egrep  -i "error" |egrep -iv "(failed with error -22)|(ERST: Error Record)|(ACPI ERROR)" '
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system('echo "%s----------\n%s" >> %s/dmesg.log' % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/dmesg.log" % (i, cluster_log_dir ))
    error = '系统日志dmesg有报错信息或个别服务器返回异常'
    info = '系统日志dmesg文件正常'
    ret = log_output('dmesg', error, info)
    return ret

# 系统负载检查
def check_loadavg():
    # print "INFO:开始检查所有节点的平均负载"
    os.system('echo "%s: %s INFO:开始检查所有节点的平均负载" >> %s ' % (cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/load.log ; touch %s/load.log' % (cluster_log_dir, cluster_log_dir))
    cmd = "awk '{if($1>50 && $2>50 && $3>50) print $1,$2,$3}' /proc/loadavg"
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s load is [%s]' >> %s/load.log" % (i, ret_dic[i], cluster_log_dir))
                os.system("echo '%s' >> %s/load.log" % (i, LOG_DIR))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/load.log" % (i, cluster_log_dir ))
    error = '个别服务器平均负载异常或个别服务器返回异常'
    info = '所有节点负载正常'
    ret = log_output('load', error, info)
    return ret

# 磁盘空间使用率率检查
def check_disk_use():
    # print "INFO:开始检查所有节点的磁盘使用率"
    os.system('echo "%s: %s INFO:开始检查所有节点的磁盘使用率" >> %s ' % (cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/disk_use.log ; touch %s/disk_use.log' % (cluster_log_dir, cluster_log_dir))
    cmd = '''df |grep -E 'data*|/'|awk '{r=$3/$2*100;if(r>94) print "dir:"$6 " disk used:"r"%"}' || :'''
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s----------%s' >> %s/disk_use.log" % (i, ret_dic[i], cluster_log_dir))
                os.system("echo '%s' >> %s/disk_use.log" % (i, LOG_DIR))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/disk_use.log" % (i, cluster_log_dir ))
    error = '个别服务器磁盘使用率异常或个别服务器返回异常'
    info = '所有节点磁盘使用率正常'
    ret = log_output('disk_use', error, info)
    return ret

# 磁盘inode利用率检查
def check_inode_use():
    # print "INFO:开始检查所有节点的磁盘inode使用率"
    os.system('echo "%s: %s INFO:开始检查所有节点的磁盘inode使用率" >> %s ' % (cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/inode.log ; touch %s/inode.log' % (cluster_log_dir, cluster_log_dir))
    cmd = '''df -i|grep -E 'data*|/' |awk '{print "dir:"$6 " inode used:"$5}'|grep -E '([7-9][0-9]|100)%' || : '''
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s----------%s' >> %s/inode.log" % (i, ret_dic[i], cluster_log_dir))
                os.system("echo '%s' >> %s/inode.log" % (i, LOG_DIR))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/inode.log" % (i, cluster_log_dir ))
    error = '个别服务器磁盘inode使用率异常或个别服务器返回异常'
    info = '所有节点磁盘inode使用率正常'
    ret = log_output('inode', error, info)
    return ret

def check_mem_use():
    # print "INFO:开始检查所有节点的内存使用率"
    os.system('echo "%s: %s INFO:开始检查所有节点的内存使用率" >> %s ' % (cluster_name, CHECK_TIME, check_log))
    os.system('rm -f %s/mem.log ; touch %s/mem.log' % (cluster_log_dir, cluster_log_dir))
    cmd = '''free -m|grep "Mem"|awk '{if(($3-$7-$6)/$2 > 0.95) print ($3-$7-$6)/$2}' '''
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s memory usage is %s' >> %s/mem.log" % (i, ret_dic[i], cluster_log_dir))
                os.system("echo '%s' >> %s/mem.log" % (i, LOG_DIR))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/mem.log" % (i, cluster_log_dir ))
    error = '个别服务器内存使用率异常或个别服务器返回异常'
    info = '所有节点内存使用率正常'
    ret = log_output('mem', error, info)
    return ret

def check_swap_use():
    # print "INFO:开始检查所有节点的swap使用率"
    os.system('echo "%s: %s INFO:开始检查所有节点的swap使用率" >> %s ' % (cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/swap.log ; touch %s/swap.log' % (cluster_log_dir, cluster_log_dir))
    cmd = '''free -m|grep "Swap"|awk '{if($2!=0 && $3/$2 > 0.2) {print $3/$2} }' '''
    # cmd = '''free -m|grep "Swap"|awk '{if($2!=0 && $3/$2 > 0.2) {print $3/$2}  else if($2==0) {print "no swap"}}' '''
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s swap usage is %s' >> %s/swap.log" % (i, ret_dic[i], cluster_log_dir))
                os.system("echo '%s' >> %s/swap.log" % (i, LOG_DIR))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/swap.log" % (i, cluster_log_dir ))
    error = '个别服务器swap使用率异常或个别服务器返回异常'
    info = '所有节点swap使用率正常'
    ret = log_output('swap', error, info)
    return ret

def check_bandwidth():
    # print "INFO:开始检查所有节点的网卡带宽制式"
    os.system('echo "%s: %s INFO:开始检查所有节点的网卡带宽制式" >> %s ' % (cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/bandwidth.log ; touch %s/bandwidth.log' % (cluster_log_dir, cluster_log_dir))
    """
    for i in ip_list:
        cmd = "ethtool `ifconfig |grep %s -B 1 |head -1|awk '{print $1} '`|grep Speed|awk -F ':' '{print $2}'|awk -F 'M' '{if ($1 < 1000) print $1}'" % i
        ret_dic = CLIENT.cmd(i, 'cmd.run', [cmd])
        if ret_dic:
            if ret_dic[i]:
                os.system("echo '%s bandwidth is %sM' >> %s/bandwidth.log" % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/bandwidth.log" % (i, cluster_log_dir ))
    """
    cmd = """ls > /dev/null;net=`ip -o -4 a |grep "inet 172."| awk -F '[: ]+' '{print $2}'|head -1`;if [ $net == bond0 ]; then cat /proc/net/bonding/bond0 | awk '{arry[NR]=$0;if($1=="Speed:" && $2<1000){print arry[NR-2]"-----"$0}}'; elif [ $net == bond1 ]; then eth=`cat /proc/net/bonding/bond1 | awk '/Currently Active Slave:/{print $4}'`;ethtool  $eth|grep Speed|awk -F ':' '{print $2}'|awk -v eth=$eth -F "M" '($1<1000){print eth,$1}';else ethtool  $net|grep Speed|awk -F ':' '{print $2}'|awk -v eth=$net -F"M" '($1<1000){print eth,$1}';fi"""
    #cmd = """for eth in `ifconfig |cut -d" " -f1|grep -v lo`;do ethtool  $eth|grep Speed|awk -F ':' '{print $2}'|awk -v eth=$eth -F"M" '($1<1000 && $1!=" Unknown!"){print eth,$1}';done"""
    # cmd = "ethtool `ifconfig |grep %s -B 1 |head -1|awk '{print $1} '`|grep Speed|awk -F ':' '{print $2}'|awk -F 'M' '{if ($1 < 1000) print $1}'" % i
    # cmd = """for eth in `ifconfig |cut -d" " -f1|grep -v lo`;do ethtool  $eth|grep Speed|awk -F ':' '{print $2}'|awk -v eth=$eth -F"M" '($1<1000 && $1!=" Unknown!"){print eth,$1}';done"""
    # cmd = """net=`ip -o -4 a |grep "scope global"| awk -F '[: ]+' '{print $2}'`;if [ $net == bond0 ]; then cat /proc/net/bonding/bond0 | awk '{arry[NR]=$0;if($1=="Speed:" && $2<1000){print arry[NR-2]"-----"$0}}'; elif [ $net == bond1 ]; then eth=`cat /proc/net/bonding/bond1 | awk '/Currently Active Slave:/{print $4}'`;ethtool  $eth|grep Speed|awk -F ':' '{print $2}'|awk -v eth=$eth -F"M" '($1<1000){print eth,$1}';else ethtool  $net|grep Speed|awk -F ':' '{print $2}'|awk -v eth=$net -F"M" '($1<1000){print eth,$1}';fi"""
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s bandwidth is %sM' >> %s/bandwidth.log" % (i, ret_dic[i], cluster_log_dir))
                os.system("echo '%s' >> %s/bandwidth.log" % (i, LOG_DIR))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/bandwidth.log" % (i, cluster_log_dir ))
    error = '个别服务器网卡带宽制式异常或个别服务器返回异常'
    info = '所有节点网卡制式正常'
    ret = log_output('bandwidth', error, info)
    return ret

def check_connect():
    # print "INFO:开始检查所有节点的连接数"
    os.system('echo "%s: %s INFO:开始检查所有节点的连接数" >> %s ' % (cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/netstat.log ; touch %s/netstat.log' % (cluster_log_dir, cluster_log_dir))
    cmd = "netstat -ant|wc -l|awk '{if($1 > 30000) print $1}' "
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s connections are %s' >> %s/netstat.log" % (i, ret_dic[i], cluster_log_dir))
                os.system("echo '%s' >> %s/netstat.log" % (i, LOG_DIR))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/netstat.log" % (i, cluster_log_dir))
    error = '个别服务器连接数超过3w异常或返回异常'
    info = '所有节点连接数正常'
    ret = log_output('netstat', error, info)
    return ret

def check_zombie():
    # print "INFO:开始检查所有节点的僵尸进程"
    os.system('echo "%s: %s INFO:开始检查所有节点的僵尸进程" >> %s ' % (cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/zombie.log ; touch %s/zombie.log' % (cluster_log_dir, cluster_log_dir))
    # cmd = "ps -ef|grep defunct|grep -v grep"
    cmd = "ps aux | egrep -w 'Z|Zz'|grep -v grep || :"
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s zombie process is %s' >> %s/zombie.log" % (i, ret_dic[i], cluster_log_dir))
                os.system("echo '%s' >> %s/zombie.log" % (i, LOG_DIR))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/zombie.log" % (i, cluster_log_dir ))
    error = '个别服务器存在僵尸进程或返回异常'
    info = '所有节点不存在僵尸进程'
    ret = log_output('zombie', error, info)
    return ret

def check_megacli():
    os.system('echo "%s: %s INFO:开始检查所有节点megacli状况" >> %s ' % (cluster_name, CHECK_TIME, check_log))
    os.system('rm -f %s/mega_errors.log ; touch %s/mega_errors.log' % (cluster_log_dir, cluster_log_dir))
    cmd = """/opt/MegaRAID/MegaCli/MegaCli64 -Pdlist -aall 2> /dev/null | awk -F ":" '{arry[$1]=$2;if($1=="Media Error Count" && $2>1000){print "Slot Number: "arry["Slot Number"]" ----- "$0} else if($1=="Other Error Count" && $2>1000){print "Slot Number: "arry["Slot Number"]" ----- "$0} else if($1=="Last Predictive Failure Event Seq Number" && $2>1000){print "Slot Number: "arry["Slot Number"]" ----- "$0} else if($1=="Drive has flagged a S.M.A.R.T alert " && $2==" Yes"){print "Slot Number: "arry["Slot Number"]" ----- "$0} else if($1=="Firmware state" && ($2==" Failed" || $2==" Unconfigured(bad)")){print "Slot Number: "arry["Slot Number"]" ----- "$0}}'"""
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system('echo "%s megacli errors:\n%s" >> %s/mega_errors.log' % (i, ret_dic[i], cluster_log_dir))
                os.system("echo '%s' >> %s/mega_errors.log" % (i, LOG_DIR))
    error = '个别服务器megacli检测到errors'
    info = 'megacli检测不存在异常'
    ret = log_output('mega_errors', error, info)
    return ret

def check_net_errors():
    os.system('echo "%s: %s INFO:开始检查所有节点网卡errors状况" >> %s ' % (cluster_name, CHECK_TIME, check_log))
    os.system('rm -f %s/net_errors.log ; touch %s/net_errors.log' % (cluster_log_dir, cluster_log_dir))
    cmd = """ifconfig |grep -E "eth|bond"  -A6|awk '{print $1,$3}'|awk -F ":" '($1=="RX errors" && $2>1000){print $0};($1=="TX errors" && $2>1000){print $0}'|sort|uniq"""
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system('echo "%s net errors:\n%s" >> %s/net_errors.log' % (i, ret_dic[i], cluster_log_dir))
                os.system("echo '%s' >> %s/net_errors.log" % (i, LOG_DIR))
    error = '个别服务器网卡检测到errors'
    info = '网卡为检测到errors'
    ret = log_output('net_errors', error, info)
    return ret

def check_bad_disk():
    # print "INFO:开始检查所有节点磁盘状况"
    os.system('echo "%s: %s IINFO:开始检查所有节点磁盘状况" >> %s ' % (cluster_name, CHECK_TIME, check_log))
    # ip_list = get_ip(cluster_name)
    os.system('rm -f %s/bad_disk.log ; touch %s/bad_disk.log' % (cluster_log_dir, cluster_log_dir))
    cmd = 'for i in `ls -d /data*`;do (touch $i/diskcheck && rm $i/diskcheck) &> /dev/null || echo $i;done'
    # cmd = 'ls / | egrep "^data[0-9]"|xargs -i touch /{}/diskcheck ; ls / | egrep "^data[0-9]"|xargs -i rm /{}/diskcheck'
    ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list', username='hadp')
    for i in ip_list:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s bad disk is %s' >> %s/bad_disk.log" % (i, ret_dic[i], cluster_log_dir ))
                os.system("echo '%s' >> %s/bad_disk.log" % (i, LOG_DIR))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/bad_disk.log" % (i, cluster_log_dir ))
    error = '个别服务器存在坏盘或返回异常'
    info = '所有节点不存在坏盘'
    ret1 = log_output('bad_disk', error, info)

    os.system('rm -f %s/miss_disk.log ; touch %s/miss_disk.log' % (cluster_log_dir, cluster_log_dir))
    # cmd1 = 'grep data /etc/fstab|grep -v "#"|wc -l'
    cmd1 = 'grep data /etc/fstab|wc -l'
    cmd2 = 'df -h|grep data|wc -l'
    ret_dic1 = CLIENT.cmd(ip_list, 'cmd.run', [cmd1], expr_form='list')
    ret_dic2 = CLIENT.cmd(ip_list, 'cmd.run', [cmd2], expr_form='list')
    for i in ip_list:
        if ret_dic1.has_key(i):
            if ret_dic1[i] > ret_dic2[i]:
                os.system("echo '%s has missed disk' >> %s/miss_disk.log" % (i, cluster_log_dir ))
                os.system("echo '%s' >> %s/miss_disk.log" % (i, LOG_DIR))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/miss_disk.log" % (i, cluster_log_dir ))
    error = '个别服务器存在掉盘或返回异常'
    info = '所有节点不存在掉盘'
    ret2 = log_output('miss_disk', error, info)
    if (ret1 + ret2):
        return ret1 + ret2
    else:
        return 0

if __name__ == '__main__':
    URL = "bdp.jd.com"
    GIT_DIR = '/job/git/hbase/'
    LOG_DIR = '/job/log/'
    ERROR_LOG = '/job/log/ERROR.log'
    NOW = datetime.datetime.now()
    TIME_STRING = NOW.strftime("%Y-%m-%d %H:%M:%S")
    CHECK_TIME = NOW.strftime("%Y-%m-%d %H:%M")
    TIMESTAMP = int(time.time()*1000)
    CLIENT = salt.client.LocalClient()
    os.system('cd %s && git pull &> /dev/null' % GIT_DIR)
    NAME_LIST_ALL = os.listdir(GIT_DIR)
    NAME_LIST_NO = ['.git', 'README.md', '_public', 'ladon-o', 'sleep', 'eagle', 'eagle_cattle', 'eagle_major', 'auto-test', 'auto-test_major', 'auto-test_wdl', 'koala', 'sleep_1.1.2', 'ant', 'elephant', 'sleep_0.94', 'vesta', 'vesta_r', 'pan_0.94']
    NAME_LIST = list(set(NAME_LIST_ALL).difference(set(NAME_LIST_NO)))
    LOG_VALUE = []
    SUM_VALUE = []
    p_name = 'hbase'

    for cluster_name in NAME_LIST:
        cluster_log_dir = LOG_DIR + cluster_name
        if not os.path.exists(cluster_log_dir):
            os.system('mkdir -p ' + cluster_log_dir)
        check_log = LOG_DIR + cluster_name + '/' + 'CHECK.log'
        (ip_list, r_alive) = get_ip_alive(cluster_name)
        if not ip_list:
            continue
        os.system('echo "%s: %s 开始检查----------------------------" >> %s' % (cluster_name, CHECK_TIME, check_log))
        # r_alive = check_alive()
        send_phenix(cluster_name, '集群内机器存活状态', r_alive, 'i')
        # print cluster_name + ' alive finish'
        r_md5 = check_md5()
        for i in range(3):
            if r_md5 > 20:
                r_md5 = check_md5()
            else:
                break
        # print r_md5
        send_phenix(cluster_name, '配置文件一致性', r_md5, 'i')
        # print cluster_name + ' md5 finish'
        r_service = check_service()
        if r_service > 20:
            r_service = check_service()
        send_phenix(cluster_name, '基础服务状态', r_service, 'i')
        # print cluster_name + ' service  finish'
        r_loadavg = check_loadavg()
        if r_loadavg > 20:
            r_loadavg = check_loadavg()
        send_phenix(cluster_name, 'CPU负载', r_loadavg, 'i')
        # print cluster_name + ' loadavg  finish'
        r_mem_use = check_mem_use()
        if r_mem_use > 20:
            r_mem_use = check_mem_use()
        send_phenix(cluster_name, '内存使用率', r_mem_use, 'i')
        # print cluster_name + ' mem  finish'
        r_disk_use = check_disk_use()
        if r_disk_use > 20:
            r_disk_use = check_disk_use()
        send_phenix(cluster_name, '磁盘使用率', r_disk_use, 'i')
        # print cluster_name + ' disk_use  finish'
        r_inode_use = check_inode_use()
        if r_inode_use > 20:
            r_inode_use = check_inode_use()
        send_phenix(cluster_name, 'inode使用率', r_inode_use, 'i')
        # print cluster_name + ' inode_use  finish'
        r_bad_disk = check_bad_disk()
        if r_bad_disk > 20:
            r_bad_disk = check_bad_disk()
        send_phenix(cluster_name, '坏盘情况', r_bad_disk, 'i')
        # print cluster_name + ' bad_disk  finish'
        r_swap_use = check_swap_use()
        if r_swap_use > 20:
            r_swap_use = check_swap_use()
        send_phenix(cluster_name, 'swap使用', r_swap_use, 'i')
        # print cluster_name + ' swap  finish'
        r_bandwidth = check_bandwidth()
        if r_bandwidth > 20:
            r_bandwidth = check_bandwidth()
        send_phenix(cluster_name, '带宽制式', r_bandwidth, 'i')
        # print cluster_name + ' bandwidth  finish'
        r_connect = check_connect()
        if r_connect > 20:
            r_connect = check_connect()
        send_phenix(cluster_name, '连接数', r_connect, 'i')
        # print cluster_name + ' connect  finish'
        r_zombie = check_zombie()
        if r_zombie > 20:
            r_zombie = check_zombie()

        send_phenix(cluster_name, '僵尸进程', r_zombie, 'i')
        # print cluster_name + ' zombie  finish'
        r_mega_errors = check_megacli()
        if r_mega_errors > 20:
            r_mega_errors = check_megacli()

        r_net_errors = check_net_errors()
        if r_net_errors > 20:
            r_net_errors = check_net_errors()
        os.system('echo "%s: %s 检查结束----------------------------" >> %s' % (cluster_name, CHECK_TIME, check_log))
        SUM_VALUE.append((TIME_STRING, p_name, cluster_name, r_alive, r_md5, r_service, r_loadavg, r_mem_use, r_disk_use, r_inode_use, r_bad_disk, r_mega_errors, r_swap_use, r_bandwidth, r_net_errors, r_connect, r_zombie))

    try:
        conn = MySQLdb.Connect(host='172.22.178.98', user='root', passwd='hadoop', db='ja_hbase',charset='utf8')
        cur=conn.cursor()
        cur.executemany('insert into hbase_check_log (start_time, p_name, cluster_name, check_itme, check_result, log_location) values(%s,%s,%s,%s,%s,%s)',LOG_VALUE)
        cur.executemany('insert into hbase_check_sum (start_time, p_name, cluster_name, alive, md5, service, loadavg, mem_use, disk_use, inode_use, bad_disk, mega_errors, swap_use, bandwidth, net_errors, connect, zombie) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',SUM_VALUE)
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        os.system('echo "Mysql Error %d: %s" >> %s ' % (e.args[0], e.args[1], ERROR_LOG))


    


