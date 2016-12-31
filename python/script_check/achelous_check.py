#!/usr/bin/env python
# encoding: utf-8

"""
@description: hbase集群巡检脚本
@author: wangdelong
@createtime: 2016/4/19 0019
@updatetime: 2016/5/5
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

def get_ip(CLUSTER_NAME):
    # 根据集群名称，获取tag_id
    url_tag_api = "http://bdp.jd.com/ops/api/server/findAllTags.ajax?tagType=2&appKey=123456&erp=wangdelong5"
    time.sleep(0.01)
    page1 = urllib.urlopen(url_tag_api)
    data1 = json.load(page1)
    data_list1 = data1['data']['dataList']
    tag_id = ''
    for i in range(0, len(data_list1)):
        if data_list1[i]['name'] == CLUSTER_NAME:
            tag_id = data_list1[i]['id']
    if not tag_id:
        sys.exit()

    # 根据tag_id获取集群的各部分地址列表
    # tag_dic = {'ns1': 25, 'ns2': 26, 'ns3': 31, 'ns4': 32, 'ns5': 33, 'dn': 7, 'jh': 11, 'jn': 9, 'zk': 10,'metastore': 24}
    # tag_dic = {'ns1': 25, 'ns2': 26, 'ns3': 31, 'ns4': 32, 'ns5': 33, 'dn': 7, 'ns1_jn': 27, 'ns2_jn': 28, 'ns3_jn': 39, 'ns4_jn': 40}
    tag_dic = {'ns1': 25, 'ns2': 26, 'ns3': 31, 'ns4': 32, 'ns5': 33, 'dn': 7}
    tag_list = ['ns1', 'ns2', 'ns3', 'ns4', 'ns5', 'dn']
    ip_dic = {}
    for i, n in tag_dic.iteritems():
        url = "http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=18,%s,%s&appKey=123456&erp=wangdelong5" % (n, tag_id)
        time.sleep(0.01)
        page = urllib.urlopen(url)
        data = json.load(page)
        data_list = data['data']['dataList']
        ip_list = []
        for m in range(0, len(data_list)):
            ip_list.append(data_list[m]['ip'])
        ip_dic[i] = ip_list
    ip_all_list = []
    # print ip_dic.keys()
    for i in tag_list:
        ip_all_list.extend(ip_dic[i])
    # for v in ip_dic.itervalues():
    #     ip_all_list.extend(v)
    # ip_all = list(set(ip_all_list))
    # print ip_all_list

    os.system('echo "%s: %s INFO:开始检查所有节点的存活状态" >> %s ' % (CLUSTER_NAME, CHECK_TIME, check_log))
    os.system('rm -f %s/alive.log ; touch %s/alive.log' % (cluster_log_dir, cluster_log_dir))
    ret_dic = CLIENT.cmd(ip_all_list, 'test.ping', expr_form='list')
    ip_alive = ret_dic.keys()
    ip_no_alive = list(set(ip_all_list).difference(set(ip_alive)))
    # print ip_no_alive
    if ip_no_alive:
        for i in ip_no_alive:
            os.system("echo '%s can not be connected' >> %s/alive.log" % (i, cluster_log_dir))
        for k in ip_dic.iterkeys():
            ip_dic[k] = list(set(ip_dic[k]).difference(set(ip_no_alive)))
    error = '集群内个别服务器salt无法连通'
    info = '集群内节点存活状态正常'
    ret = log_output('alive', error, info)
    # print ret
    return ip_alive, ip_dic, ret

# 打印输出日志，记录数据库输入信息（LOG_VALUE）
def log_output(check_name, error, info):
    (s, r) = commands.getstatusoutput("cat %s/%s.log |grep -v salt | wc -l" % (cluster_log_dir, check_name))
    if int(r):
        os.system('echo "%s: %s ERROR:%s（%s/%s.log）" >> %s ' % (CLUSTER_NAME, CHECK_TIME, error, cluster_log_dir, check_name, check_log))
        os.system('echo "%s: %s ERROR:%s（%s/%s.log）" >> %s ' % (CLUSTER_NAME, CHECK_TIME, error, cluster_log_dir, check_name, ERROR_LOG))
        ret_tuple = (TIME_STRING, CLUSTER_NAME, check_name, 1,cluster_log_dir + '/' + check_name + '.log')
    else:
        os.system('echo "%s: %s INFO:%s" >> %s ' % (CLUSTER_NAME, CHECK_TIME, info, check_log))
        os.system('rm -rf %s/%s.log' % (cluster_log_dir, check_name))
        ret_tuple = (TIME_STRING, CLUSTER_NAME, check_name, 0,'')
    LOG_VALUE.append(ret_tuple)
    return int(r)

# 上报phenix
def send_phenix(CLUSTER_NAME, metricK, metricV, dt):
    params = {'monitorData' : json.dumps({'mr': 'ifspeed_monitor','tp': '004','t': TIMESTAMP ,'lc': {'s_1_k': '集群巡检结果' ,'s_1_n': '集群巡检结果'}, 'me':  [{'lc': {'s_1_k': CLUSTER_NAME ,'s_1_n': CLUSTER_NAME}, 'me':  [{'k': metricK,'v': metricV,'n': metricK,'dt': dt}]}]})}
    headerdata = {"Content-Type":"application/x-www-form-urlencoded", "Connection":"Keep-Alive"}
    server = httplib.HTTPConnection(URL)
    server.request("POST","/phenix/collector/monitorData.ajax",urllib.urlencode(params),headerdata)
    time.sleep(0.1)
    response = server.getresponse()
    # print CLUSTER_NAME, response.status
    # print response.reason
    # print response.read()
    server.close()

# def check_alive():
#     os.system('echo "%s: %s INFO:开始检查所有节点的存活状态" >> %s ' % (CLUSTER_NAME, CHECK_TIME, check_log))
#     os.system('rm -f %s/alive.log ; touch %s/alive.log' % (cluster_log_dir, cluster_log_dir))
#     ret_dic = CLIENT.cmd(ip_all, 'test.ping', expr_form='list')
#     ip_list_alive = ret_dic.keys()
#     ip_no_alive = list(set(ip_all).difference(set(ip_list_alive)))
#     if ip_no_alive:
#         for i in ip_no_alive:
#             os.system("echo '%s salt can not be connected' >> %s/alive.log" % (i, cluster_log_dir))
#     error = '集群内个别服务器salt无法连通'
#     info = '集群内节点存活状态正常'
#     ret = log_output('alive', error, info)
#     return ret

#执行文件一致性检查
def check_md5():
    os.system('echo "%s: %s INFO:开始检查所有节点的配置文件一致性" >> %s ' % (CLUSTER_NAME, CHECK_TIME, check_log))
    ns_md5_dic = {}
    ns_tuple = ('ns1', 'ns2', 'ns3', 'ns4', 'ns5')
    # 初始化ns配置
    for i in ns_tuple:
        md5_dic = {}
        conf_list = []
        base_dir = '/software/servers/hadoop-2.2.0/etc/hadoop'
        top = GIT_DIR + CLUSTER_NAME + '/' + i
        dir_num = len(top)
        for root, dirs, files in os.walk(top, topdown=True):
            for name in files:
                conf_list.append(os.path.join(root, name)[dir_num:])

        for n in conf_list:#将md5校验值加入字典
            (s, r)=commands.getstatusoutput("md5sum %s%s | awk '{print $1}'" % (top, n))
            md5_dic[base_dir + n] = r
        ns_md5_dic[i] = md5_dic
    # print "ns_md5_dic 初始化完成"
    # print ns_md5_dic

    # 初始化jn配置
    '''
    jn_md5_dic = {}
    jn_tuple = ('ns1_jn', 'ns2_jn', 'ns3_jn', 'ns4_jn')
    for i in jn_tuple:
        md5_dic = {}
        conf_list = []
        base_dir = '/software/servers/hadoop-2.2.0/etc/hadoop'
        top = GIT_DIR + CLUSTER_NAME + '/' + i + '/etc/hadoop'
        dir_num = len(top)
        for root, dirs, files in os.walk(top, topdown=True):
            for name in files:
                conf_list.append(os.path.join(root, name)[dir_num:])

        for n in conf_list:  # 将md5校验值加入字典
            (s, r) = commands.getstatusoutput("md5sum %s%s | awk '{print $1}'" % (top, n))
            md5_dic[base_dir + n] = r
        jn_md5_dic[i] = md5_dic
    # print jn_md5_dic.keys()
    '''
    # print "初始化jn完成"

    pub_md5_dic = {}
    pub_conf_list = []
    pub_base_dir = '/software/servers/hadoop-2.2.0/etc/hadoop'
    pub_top = GIT_DIR + CLUSTER_NAME + '/public/software/etc/hadoop'
    dir_num = len(pub_top)
    for root, dirs, files in os.walk(pub_top, topdown=True):
        for name in files:
            pub_conf_list.append(os.path.join(root, name)[dir_num:])
    for n in pub_conf_list:  # 将md5校验值加入字典
        (s, r) = commands.getstatusoutput("md5sum %s%s | awk '{print $1}'" % (pub_top, n))
        pub_md5_dic[pub_base_dir + n] = r
    # print "pub_md5_dic public初始化完成"
    # print pub_md5_dic['/software/servers/hadoop-2.2.0/etc/nm_conf/hosts/mapred_hosts']

    host_path = GIT_DIR + CLUSTER_NAME + '/etc/hosts'
    host_md5 = commands.getoutput("md5sum %s | awk '{print $1}'" % host_path)
    pub_md5_dic['/etc/hosts'] = host_md5

    yarn_bashrc_path = GIT_DIR + CLUSTER_NAME + '/ssh_keys/yarn_bashrc'
    yarn_bashrc_md5 = commands.getoutput("md5sum %s | awk '{print $1}'" % yarn_bashrc_path)
    pub_md5_dic['/home/yarn/.bashrc'] = yarn_bashrc_md5

    hadp_bashrc_path = GIT_DIR + CLUSTER_NAME + '/ssh_keys/hadp_bashrc'
    hadp_bashrc_md5 = commands.getoutput("md5sum %s | awk '{print $1}'" % hadp_bashrc_path)
    pub_md5_dic['/home/hadp/.bashrc'] = hadp_bashrc_md5
    # print "pub_md5_dic bashrc初始化完成"
    # print pub_md5_dic['/home/hadp/.bashrc']

    dn_md5_dic = {}
    dn_conf_list = []
    dn_base_dir = '/software/servers/hadoop-2.2.0/etc/nm_conf'
    dn_top = GIT_DIR + CLUSTER_NAME + '/public/software/etc/nm_conf'
    dir_num = len(dn_top)
    for root, dirs, files in os.walk(dn_top, topdown=True):
        for name in files:
            dn_conf_list.append(os.path.join(root, name)[dir_num:])
    for n in dn_conf_list:  # 将md5校验值加入字典
        (s, r) = commands.getstatusoutput("md5sum %s%s | awk '{print $1}'" % (dn_top, n))
        dn_md5_dic[dn_base_dir + n] = r
    # rm_md5_dic = {}
    # rm_conf_list = []
    # rm_base_dir = '/software/servers/hadoop-2.2.0/etc/nm_conf'
    # top = GIT_DIR + CLUSTER_NAME + '/rm'
    # dir_num = len(top)
    # for root, dirs, files in os.walk(top, topdown=True):
    #     for name in files:
    #         rm_conf_list.append(os.path.join(root, name)[dir_num:])
    # for n in rm_conf_list:  # 将md5校验值加入字典
    #     (s, r) = commands.getstatusoutput("md5sum %s%s | awk '{print $1}'" % (top, i))
    #     rm_md5_dic[rm_base_dir + n] = r
    mem_md5_dic = {}
    mem_64g_path = GIT_DIR + CLUSTER_NAME + '/mem_64g/yarn-site.xml'
    mem_64g_md5 = commands.getoutput("md5sum %s | awk '{print $1}'" % mem_64g_path)
    mem_md5_dic[64] = mem_64g_md5
    mem_128g_path = GIT_DIR + CLUSTER_NAME + '/mem_128g/yarn-site.xml'
    mem_128g_md5 = commands.getoutput("md5sum %s | awk '{print $1}'" % mem_128g_path)
    mem_md5_dic[128] = mem_128g_md5
    os.system('rm -f %s/md5.log ; touch %s/md5.log' % (cluster_log_dir, cluster_log_dir))
    # 判断public配置
    for conf, md5 in pub_md5_dic.iteritems():
        cmd = "md5sum " + conf + " | awk '{print $1}' "
        ret_dic = CLIENT.cmd(ip_alive, 'cmd.run', [cmd], expr_form='list')
        for i in ip_alive:
            if ret_dic.has_key(i):
                if ret_dic[i] != md5:
                    os.system("echo '%s  %s' >> %s/md5.log" % (i, conf, cluster_log_dir ))
            else:
                os.system("echo '%s salt-minon can not be connected!' >> %s/md5.log" % (i, cluster_log_dir ))
    # 判断内存及yarn-site
    mem_cmd = "md5sum /software/servers/hadoop-2.2.0/etc/hadoop/yarn-site.xml | awk '{print $1}' "
    mem_ret_dic = CLIENT.cmd(ip_alive, ['grains.item','cmd.run'], [['mem_total'],[mem_cmd]], expr_form='list')
    for i in ip_alive:
        if mem_ret_dic.has_key(i):
            if mem_ret_dic[i]['grains.item']['mem_total'] < 65000:
                if mem_ret_dic[i]['cmd.run'] != mem_md5_dic[64]:
                    os.system("echo '%s  /software/servers/hadoop-2.2.0/etc/hadoop/yarn-site.xml (64G)' >> %s/md5.log" % (i, cluster_log_dir))
            else:
                if mem_ret_dic[i]['cmd.run'] != mem_md5_dic[128]:
                    os.system("echo '%s  /software/servers/hadoop-2.2.0/etc/hadoop/yarn-site.xml (128G)' >> %s/md5.log" % (i, cluster_log_dir))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/md5.log" % (i, cluster_log_dir))
    # print "判断public配置完成"
    # 判断dn节点
    for conf, md5 in dn_md5_dic.iteritems():
        cmd = "md5sum " + conf + " | awk '{print $1}' "
        ret_dic = CLIENT.cmd(ip_alive, 'cmd.run', [cmd], expr_form='list')
        for i in ip_dic['dn']:
            if ret_dic.has_key(i):
                if ret_dic[i] != md5:
                    os.system("echo '%s  %s' >> %s/md5.log" % (i, conf, cluster_log_dir))
            else:
                os.system("echo '%s salt-minon can not be connected!' >> %s/md5.log" % (i, cluster_log_dir))
    # print "判断dn配置完成"
    # 判断ns1-ns5
    for ns in ns_tuple:
        ip_list = ip_dic[ns]
        for conf, md5 in ns_md5_dic[ns].iteritems():
            cmd = "md5sum " + conf + " | awk '{print $1}' "
            ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
            for i in ip_list:
                if ret_dic.has_key(i):
                    if ret_dic[i] != md5:
                        os.system("echo '%s  %s' >> %s/md5.log" % (i, conf, cluster_log_dir))
                else:
                    os.system("echo '%s salt-minon can not be connected!' >> %s/md5.log" % (i, cluster_log_dir))
    # print "判断ns1-ns5配置完成"

    # 判断jn
    '''
    for jn in jn_tuple:
        ip_list = ip_dic[jn]
        for conf, md5 in jn_md5_dic[jn].iteritems():
            cmd = "md5sum " + conf + " | awk '{print $1}' "
            ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
            for i in ip_list:
                if ret_dic.has_key(i):
                    if ret_dic[i] != md5:
                        os.system("echo '%s  %s' >> %s/md5.log" % (i, conf, cluster_log_dir))
                else:
                    os.system("echo '%s salt-minon can not be connected!' >> %s/md5.log" % (i, cluster_log_dir))
    '''
    # print "判断jn配置完成"

    error = '个别服务器配置文件不一致或个别服务器返回异常'
    info = '集群内节点配置文件一致性检查正常'
    ret = log_output('md5', error, info)
    return ret

# 基础服务安装检查
def check_service():
    os.system('echo "%s: %s INFO:开始检查所有节点的基础服务状态（crond snmpd gmond sshd rsyslog sysstat）" >> %s ' % (CLUSTER_NAME, CHECK_TIME, check_log))
    os.system('rm -f %s/service.log ; touch %s/service.log' % (cluster_log_dir, cluster_log_dir))
    cmd = "for i in crond snmpd gmond sshd rsyslog sysstat; do service $i status; done |grep -v pid"
    ret_dic = CLIENT.cmd(ip_alive, 'cmd.run', [cmd], expr_form='list')
    for i in ip_alive:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s  %s' >> %s/service.log" % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/service.log" % (i, cluster_log_dir ))
    error = '个别基础服务未安装(未运行)或个别服务器返回异常'
    info = '集群内节点基础服务状态正常'
    ret = log_output('service', error, info)
    return ret

# 系统日志错误检查
def check_messages():
    os.system('echo "%s: %s INFO:开始检查所有节点系统日志messages文件" >> %s ' % (CLUSTER_NAME, CHECK_TIME, check_log))
    os.system('rm -f %s/message.log ; touch %s/message.log' % (cluster_log_dir, cluster_log_dir))
    cmd = '''cat /var/log/messages |egrep  "fail|error" | egrep -iv "ACPI Error" '''
    ret_dic = CLIENT.cmd(ip_alive, 'cmd.run', [cmd], expr_form='list')
    for i in ip_alive:
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
    os.system('echo "%s: %s INFO:开始检查所有节点系统日志dmesg文件" >> %s ' % (CLUSTER_NAME, CHECK_TIME, check_log))
    os.system('rm -f %s/dmesg.log ; touch %s/dmesg.log' % (cluster_log_dir, cluster_log_dir))
    cmd = 'dmesg |egrep  -i "error" |egrep -iv "(failed with error -22)|(ERST: Error Record)|(ACPI ERROR)" '
    ret_dic = CLIENT.cmd(ip_alive, 'cmd.run', [cmd], expr_form='list')
    for i in ip_alive:
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
    os.system('echo "%s: %s INFO:开始检查所有节点的平均负载" >> %s ' % (CLUSTER_NAME, CHECK_TIME, check_log))
    os.system('rm -f %s/load.log ; touch %s/load.log' % (cluster_log_dir, cluster_log_dir))
    cmd = "awk '{if($1>100 && $2>100 && $3>100) print $1,$2,$3}' /proc/loadavg"
    ret_dic = CLIENT.cmd(ip_alive, 'cmd.run', [cmd], expr_form='list')
    for i in ip_alive:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s load is [%s]' >> %s/load.log" % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/load.log" % (i, cluster_log_dir ))
    error = '个别服务器平均负载异常或个别服务器返回异常'
    info = '所有节点负载正常'
    ret = log_output('load', error, info)
    return ret

# 磁盘空间使用率率检查
def check_disk_use():
    os.system('echo "%s: %s INFO:开始检查所有节点的磁盘使用率" >> %s ' % (CLUSTER_NAME, CHECK_TIME, check_log))
    os.system('rm -f %s/disk_use.log ; touch %s/disk_use.log' % (cluster_log_dir, cluster_log_dir))
    cmd = '''df -h|grep -E 'data*|/'|awk '{print "dir:"$6 " disk used:"$5}'|grep -E '([9][5-9]|100)%' '''
    ret_dic = CLIENT.cmd(ip_alive, 'cmd.run', [cmd], expr_form='list')
    for i in ip_alive:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s----------%s' >> %s/disk_use.log" % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/disk_use.log" % (i, cluster_log_dir ))
    error = '个别服务器磁盘使用率异常或个别服务器返回异常'
    info = '所有节点磁盘使用率正常'
    ret = log_output('disk_use', error, info)
    return ret

# 磁盘inode利用率检查
def check_inode_use():
    os.system('echo "%s: %s INFO:开始检查所有节点的磁盘inode使用率" >> %s ' % (CLUSTER_NAME, CHECK_TIME, check_log))
    os.system('rm -f %s/inode.log ; touch %s/inode.log' % (cluster_log_dir, cluster_log_dir))
    cmd = '''df -i|grep -E 'data*|/' |awk '{print "dir:"$6 " inode used:"$5}'|grep -E '([7-9][0-9]|100)%' '''
    ret_dic = CLIENT.cmd(ip_alive, 'cmd.run', [cmd], expr_form='list')
    for i in ip_alive:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s----------%s' >> %s/inode.log" % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/inode.log" % (i, cluster_log_dir ))
    error = '个别服务器磁盘inode使用率异常或个别服务器返回异常'
    info = '所有节点磁盘inode使用率正常'
    ret = log_output('inode', error, info)
    return ret

def check_mem_use():
    os.system('echo "%s: %s INFO:开始检查所有节点的内存使用率" >> %s ' % (CLUSTER_NAME, CHECK_TIME, check_log))
    os.system('rm -f %s/mem.log ; touch %s/mem.log' % (cluster_log_dir, cluster_log_dir))
    cmd = '''free -m|grep "Mem"|awk '{if(($3-$7-$6)/$2 > 0.9) print ($3-$7-$6)/$2}' '''
    ret_dic = CLIENT.cmd(ip_alive, 'cmd.run', [cmd], expr_form='list')
    for i in ip_alive:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s memory usage is %s' >> %s/mem.log" % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/mem.log" % (i, cluster_log_dir ))
    error = '个别服务器内存使用率异常或个别服务器返回异常'
    info = '所有节点内存使用率正常'
    ret = log_output('mem', error, info)
    return ret

def check_swap_use():
    os.system('echo "%s: %s INFO:开始检查所有节点的swap使用率" >> %s ' % (CLUSTER_NAME, CHECK_TIME, check_log))
    os.system('rm -f %s/swap.log ; touch %s/swap.log' % (cluster_log_dir, cluster_log_dir))
    cmd = '''free -m|grep "Swap"|awk '{if($2!=0 && $3/$2 > 0.25) {print $3/$2}}' '''
    # cmd = '''free -m|grep "Swap"|awk '{if($2!=0 && $3/$2 > 0.25) {print $3/$2}  else if($2==0) {print "no swap"}}' '''
    ret_dic = CLIENT.cmd(ip_alive, 'cmd.run', [cmd], expr_form='list')
    for i in ip_alive:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s swap usage is %s' >> %s/swap.log" % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/swap.log" % (i, cluster_log_dir ))
    error = '个别服务器swap使用率异常或个别服务器返回异常'
    info = '所有节点swap使用率正常'
    ret = log_output('swap', error, info)
    return ret

def check_bandwidth():
    os.system('echo "%s: %s INFO:开始检查所有节点的网卡带宽制式" >> %s ' % (CLUSTER_NAME, CHECK_TIME, check_log))
    os.system('rm -f %s/bandwidth.log ; touch %s/bandwidth.log' % (cluster_log_dir, cluster_log_dir))
    for i in ip_alive:
        cmd = "ethtool `ifconfig |grep %s -B 1 |head -1|awk '{print $1} '`|grep Speed|awk -F ':' '{print $2}'|awk -F 'M' '{if ($1 < 1000) print $1}'" % i
        ret_dic = CLIENT.cmd(i, 'cmd.run', [cmd])
        if ret_dic:
            if ret_dic[i]:
                os.system("echo '%s bandwidth is %sM' >> %s/bandwidth.log" % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/bandwidth.log" % (i, cluster_log_dir ))
    error = '个别服务器网卡带宽制式异常或个别服务器返回异常'
    info = '所有节点网卡制式正常'
    ret = log_output('bandwidth', error, info)
    return ret

def check_connect():
    os.system('echo "%s: %s INFO:开始检查所有节点的连接数" >> %s ' % (CLUSTER_NAME, CHECK_TIME, check_log))
    os.system('rm -f %s/netstat.log ; touch %s/netstat.log' % (cluster_log_dir, cluster_log_dir))
    cmd = "netstat -ant|wc -l|awk '{if($1 > 30000) print $1}' "
    ret_dic = CLIENT.cmd(ip_alive, 'cmd.run', [cmd], expr_form='list')
    for i in ip_alive:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s connections are %s' >> %s/netstat.log" % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/netstat.log" % (i, cluster_log_dir))
    error = '个别服务器连接数超过3w异常或返回异常'
    info = '所有节点连接数正常'
    ret = log_output('netstat', error, info)
    return ret

def check_zombie():
    os.system('echo "%s: %s INFO:开始检查所有节点的僵尸进程" >> %s ' % (CLUSTER_NAME, CHECK_TIME, check_log))
    os.system('rm -f %s/zombie.log ; touch %s/zombie.log' % (cluster_log_dir, cluster_log_dir))
    # cmd = "ps -ef|grep defunct|grep -v grep"
    cmd = "ps aux | egrep -w 'Z|Zz'|grep -v grep"
    ret_dic = CLIENT.cmd(ip_alive, 'cmd.run', [cmd], expr_form='list')
    for i in ip_alive:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s zombie process is %s' >> %s/zombie.log" % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/zombie.log" % (i, cluster_log_dir ))
    error = '个别服务器存在僵尸进程或返回异常'
    info = '所有节点不存在僵尸进程'
    ret = log_output('zombie', error, info)
    return ret

def check_bad_disk():
    os.system('echo "%s: %s IINFO:开始检查所有节点磁盘状况" >> %s ' % (CLUSTER_NAME, CHECK_TIME, check_log))
    os.system('rm -f %s/bad_disk.log ; touch %s/bad_disk.log' % (cluster_log_dir, cluster_log_dir))
    cmd = 'for i in `ls -d /data*`;do (touch $i/diskcheck && rm $i/diskcheck) &> /dev/null || echo $i;done'
    ret_dic = CLIENT.cmd(ip_alive, 'cmd.run', [cmd], expr_form='list', username='hadp')
    for i in ip_alive:
        if ret_dic.has_key(i):
            if ret_dic[i]:
                os.system("echo '%s bad disk is %s' >> %s/bad_disk.log" % (i, ret_dic[i], cluster_log_dir))
        else:
            os.system("echo '%s salt-minon can not be connected!' >> %s/bad_disk.log" % (i, cluster_log_dir ))
    error = '个别服务器存在坏盘或返回异常'
    info = '所有节点不存在坏盘'
    ret1 = log_output('bad_disk', error, info)

    os.system('rm -f %s/miss_disk.log ; touch %s/miss_disk.log' % (cluster_log_dir, cluster_log_dir))
    # cmd1 = 'grep data /etc/fstab|grep -v "#"|wc -l'
    cmd1 = 'grep data /etc/fstab|wc -l'
    cmd2 = 'df -h|grep data|wc -l'
    ret_dic1 = CLIENT.cmd(ip_alive, 'cmd.run', [cmd1], expr_form='list')
    ret_dic2 = CLIENT.cmd(ip_alive, 'cmd.run', [cmd2], expr_form='list')
    for i in ip_alive:
        if ret_dic1.has_key(i):
            if ret_dic1[i] > ret_dic2[i]:
                os.system("echo '%s has missed disk' >> %s/miss_disk.log" % (i, cluster_log_dir ))
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
    GIT_DIR = '/job/git/hadoop/'
    LOG_DIR = '/job/log/'
    ERROR_LOG = '/job/log/ERROR.log'
    NOW = datetime.datetime.now()
    TIME_STRING = NOW.strftime("%Y-%m-%d %H:%M:%S")
    CHECK_TIME = NOW.strftime("%Y-%m-%d %H:%M")
    TIMESTAMP = int(time.time() * 1000)
    CLIENT = salt.client.LocalClient()
    os.system('cd %s && git pull &> /dev/null' % GIT_DIR)
    CLUSTER_NAME = 'jdw'
    LOG_VALUE = []
    SUM_VALUE = []
    cluster_log_dir = LOG_DIR + CLUSTER_NAME
    if not os.path.exists(cluster_log_dir):
        os.system('mkdir -p ' + cluster_log_dir)
    check_log = LOG_DIR + CLUSTER_NAME + '/' + 'CHECK.log'
    os.system('echo "%s: %s 开始检查----------------------------" >> %s' % (CLUSTER_NAME, CHECK_TIME, check_log))

    (ip_alive, ip_dic, r_alive) = get_ip(CLUSTER_NAME)
    # r_alive = check_alive()
    send_phenix(CLUSTER_NAME, '集群内机器存活状态', r_alive, 'i')
    # print CLUSTER_NAME + ' alive finish'
    r_md5 = check_md5()
    # if r_md5 > 50:
    #     r_md5 = check_md5()
    # print r_md5
    send_phenix(CLUSTER_NAME, '配置文件一致性', r_md5, 'i')
    # print CLUSTER_NAME + ' md5 finish'
    r_service = check_service()
    send_phenix(CLUSTER_NAME, '基础服务状态', r_service, 'i')
    # print CLUSTER_NAME + ' service  finish'
    r_loadavg = check_loadavg()
    send_phenix(CLUSTER_NAME, 'CPU负载', r_loadavg, 'i')
    # print CLUSTER_NAME + ' loadavg  finish'
    r_mem_use = check_mem_use()
    send_phenix(CLUSTER_NAME, '内存使用率', r_mem_use, 'i')
    # print CLUSTER_NAME + ' mem  finish'
    r_disk_use = check_disk_use()
    send_phenix(CLUSTER_NAME, '磁盘使用率', r_disk_use, 'i')
    # print CLUSTER_NAME + ' disk_use  finish'
    r_inode_use = check_inode_use()
    send_phenix(CLUSTER_NAME, 'inode使用率', r_inode_use, 'i')
    # print CLUSTER_NAME + ' inode_use  finish'
    r_bad_disk = check_bad_disk()
    send_phenix(CLUSTER_NAME, '坏盘情况', r_bad_disk, 'i')
    # print CLUSTER_NAME + ' bad_disk  finish'
    r_swap_use = check_swap_use()
    send_phenix(CLUSTER_NAME, 'swap使用', r_swap_use, 'i')
    # print CLUSTER_NAME + ' swap  finish'
    r_bandwidth = check_bandwidth()
    send_phenix(CLUSTER_NAME, '带宽制式', r_bandwidth, 'i')
    # print CLUSTER_NAME + ' bandwidth  finish'
    r_connect = check_connect()
    send_phenix(CLUSTER_NAME, '连接数', r_connect, 'i')
    # print CLUSTER_NAME + ' connect  finish'
    r_zombie = check_zombie()
    send_phenix(CLUSTER_NAME, '僵尸进程', r_zombie, 'i')
    # print CLUSTER_NAME + ' zombie  finish'
    # print CLUSTER_NAME + ' all finish'
    os.system('echo "%s: %s 检查结束----------------------------" >> %s' % (CLUSTER_NAME, CHECK_TIME, check_log))
    SUM_VALUE.append((TIME_STRING, CLUSTER_NAME, r_alive, r_md5, r_service, r_loadavg, r_mem_use, r_disk_use,r_inode_use, r_bad_disk, r_swap_use, r_bandwidth, r_connect, r_zombie))

    try:
        conn = MySQLdb.Connect(host='172.22.178.98', user='root', passwd='hadoop', db='ja_hbase', charset='utf8')
        cur = conn.cursor()
        cur.executemany('insert into hbase_check_log (start_time,CLUSTER_NAME,check_itme,check_result,log_location) values(%s,%s,%s,%s,%s)', LOG_VALUE)
        cur.executemany('insert into hbase_check_sum (start_time, CLUSTER_NAME, alive, md5, service, loadavg, mem_use, disk_use, inode_use, bad_disk, swap_use, bandwidth, connect, zombie) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', SUM_VALUE)
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error, e:
        os.system('echo "Mysql Error %d: %s" >> %s ' % (e.args[0], e.args[1], ERROR_LOG))

    # print '数据库插入完成'


