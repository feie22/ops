#!/usr/bin/env python
# encoding: utf-8

"""
@description: 服务器初始化
@author: wangdelong@jd.com
@createtime: 2016/8/6 0006
@updatetime: ?
"""

import sys
import time
import commands
import json
import urllib
import paramiko
import datetime

reload(sys)
sys.setdefaultencoding('utf-8')

if len(sys.argv) == 1:
    sys.exit("请输入一个集群名称")
CLUSTER_NAME = sys.argv[1]
# GIT_DIR = '/job/git/hbase/'
BASE_DIR = '/job/ops/'
# IP_FILE = BASE_DIR + "ip.list"
LOG_FILE = BASE_DIR + "exec.log"
ROSTER_FILE = BASE_DIR + "roster"
# PASSWD = '123456'
# PASSWD = '1qaz@WSX'
PASSWD = 'riy8Y_F8j5kFg_BB-2y_Wj=3T'

def write_file(file, content, w_mode='a'):
    if w_mode == 'a':
        print content,
    try:
        f = open(file, w_mode)
        f.write(content)
    except:
        sys.exit("%s文件写入失败，写入内容：%s" % (file, content))
    finally:
        f.close()

def get_ip():
    # 根据集群名称，获取tag_id
    url_tag_api = "http://bdp.jd.com/ops/api/server/findAllTags.ajax?tagType=2&appKey=123456&erp=wangdelong5"
    time.sleep(0.05)
    page1 = urllib.urlopen(url_tag_api)
    data1 = json.load(page1)
    data_list1 = data1['data']['dataList']
    tag_id = ''
    for i in range(0, len(data_list1)):
        if data_list1[i]['name'] == CLUSTER_NAME:
            tag_id = data_list1[i]['id']
    if not tag_id:
        sys.exit("集群名称错误，BDP中无此集群")
    # print "tag is %s" % tag_id

    # 根据tag_id获取集群的ip角色的字典
    tag_dic = {'NN':5, 'DN':7, 'ZK':10, 'HM':71}
    ip_dic = {}
    ip_all = []
    for j, k in tag_dic.iteritems():
        url_ip_api = "http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=19,589,%s,%s&appKey=123456&erp=wangdelong5" % (k, tag_id)
        time.sleep(0.1)
        page = urllib.urlopen(url_ip_api)
        data = json.load(page)
        data_list = data['data']['dataList']
        ip_dic[j] = []
        for i in range(0, len(data_list)):
            ip_dic[j].append(data_list[i]['ip'])
        ip_all.extend(ip_dic[j])
        content = j + "：" + str(len(ip_dic[j])) + "\n"
        write_file(LOG_FILE, content)
    if not ip_all:
        sys.exit("集群内无待上线IP")
    ip_dic['all'] = list(set(ip_all))
    content = "ALL：" + str(len(ip_dic['all'])) + "\n"
    write_file(LOG_FILE, content)
    return ip_dic

def check_connect(ip_dic):
    ip_no = []
    for ip in ip_dic['all']:
        try:
            s = paramiko.SSHClient()  # 创建ssh客户端对象
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(ip, 22, 'root', PASSWD, timeout=2, look_for_keys=False)
            s.close()
        except:
            # print '%s can not login' % ip
            ip_no.append(ip)
    if ip_no:
        ip_s = '\n'.join(ip_no)
        content = "ssh无法连通ip列表：\n" + ip_s + "\n"
        write_file(LOG_FILE, content)
        sys.exit("程序退出")
    else:
        content = "ssh连通性测试完成\n"
        write_file(LOG_FILE, content)

    # if len(ip_no) > 5:
    #     sys.exit("多于5个IP无法连通，程序终止")
    # elif len(list(set(ip_dic['NN']).difference(set(ip_no)))) < len(ip_dic['NN']) or len(list(set(ip_dic['ZK']).difference(set(ip_no)))) < len(ip_dic['ZK']):
    #     sys.exit("管理节点无法连通，程序终止")
    #
    # for i in ip_dic.itervalues():
    #     i = list(set(i).difference(set(ip_no)))
    # return ip_dic

def roster(ip_list):
    content = ''
    for i in ip_list:
        content = content + "%s:\n  host: %s\n  passwd: %s\n  timeout: 2\n" % (i, i, PASSWD)
    write_file(ROSTER_FILE, content, 'w')
    content = "roster文件生成完成\n"
    write_file(LOG_FILE, content)

    # cmd = "sh %sroster.sh" % BASE_DIR
    # (s,r) = commands.getstatusoutput(cmd)
    # if s:
    #     sys.exit("roster文件生成失败，程序退出")

def salt_exec(cmd):
    (s, r) = commands.getstatusoutput(cmd)
    if s:
        sys.exit("%s\nsalt-ssh 执行错误，程序退出" %cmd)
    r_p = r.replace('true','True')
    ret_dic = eval(r_p)
    ip_fail = []
    for i, n in ret_dic.iteritems():
        if n == 'Fail':
            ip_fail.append(i)
    return ip_fail

def init_server():
    # script位置：/srv/salt/script
    cmd_cp = "salt-ssh -i --roster-file=%s --out=json --static --max-procs=1000 \* cp.get_dir salt://script /tmp" % ROSTER_FILE
    cmd_raid0 = '''salt-ssh -i --roster-file=%s --out=json --static --max-procs=1000 \*  cmd.run "sh /tmp/Toraid0mkfs.sh &>/tmp/raid.log || echo 'Fail'" ''' % ROSTER_FILE
    cmd_raid50 = '''salt-ssh -i --roster-file=%s --out=json --static --max-procs=1000 \*  cmd.run "sh /tmp/Toraid50mkfs.sh &>/tmp/raid.log || echo 'Fail'" ''' % ROSTER_FILE
    cmd_hadoop = '''salt-ssh -i --roster-file=%s --out=json --static --max-procs=1000 \*  cmd.run "sh /tmp/hadoop_v2.sh &>/tmp/hadoop.log || echo 'Fail'" ''' % ROSTER_FILE
    cmd_cluster = '''salt-ssh -i --roster-file=%s --out=json --static --max-procs=1000 \*  cmd.run "sh /tmp/init_cluster.sh noraid hbase %s &>/tmp/init_cluster.log || echo 'Fail'" ''' % (ROSTER_FILE, CLUSTER_NAME)
    cmd_list = [cmd_cp, cmd_raid0, cmd_hadoop, cmd_cluster]
    # cmd_list = [cmd_cp, cmd_hadoop, cmd_cluster]
    now = datetime.datetime.now()
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")
    content = "--------------------服务器初始化开始 " + time_string + "--------------------\n"
    write_file(LOG_FILE, content)
    ip_dic = get_ip()
    check_connect(ip_dic)
    roster(ip_dic['all'])
    for i in cmd_list:
        ip_fail = salt_exec(i)
        if ip_fail:
            ip_s = '\n'.join(ip_fail)
            content = i + "\n执行失败ip列表：\n" + ip_s + "\n--------------------\n"
            write_file(LOG_FILE, content)
        content = i + "\n执行完成\n\n"
        write_file(LOG_FILE, content)
    now = datetime.datetime.now()
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")
    content = "--------------------服务器初始化完成 " + time_string + "--------------------\n"
    write_file(LOG_FILE, content)


if __name__ == '__main__':

    init_server()