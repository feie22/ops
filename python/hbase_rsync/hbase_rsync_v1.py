#!/usr/bin/env python
# encoding: utf-8

"""
@description: hbase集群巡检脚本
@author: wangdelong
@createtime: 2016/4/19 0019
@updatetime: 2016/5/9
"""

import os
import sys
import time
import datetime
import commands
import json
import urllib

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
        # print "ERROR:请输入正确的hbase集群名称"
        sys.exit("集群tag_id获取失败")

    # 根据tag_id获取集群的ip地址列表
    url_ip_api = "http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=19,%s&appKey=123456&erp=wangdelong5" % tag_id
    time.sleep(0.01)
    page2 = urllib.urlopen(url_ip_api)
    data2 = json.load(page2)
    data_list2 = data2['data']['dataList']
    ip_list2 = []
    for i in range(0, len(data_list2)):
        ip_list2.append(data_list2[i]['ip'])
    if not ip_list2:
        sys.exit("没有获取到集群的IP地址")

    # 获取ZK节点IP地址
    url_ip_zk = "http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=19,10,%s&appKey=123456&erp=wangdelong5" % tag_id
    time.sleep(0.01)
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

    for i in ip_list:
        (s, r) = commands.getstatusoutput('nc %s -z 22' %i)
        if s:
            print "%s can not be connected 22 port" %i
            ip_list.remove(i)
    # print ip_list
    return ip_list

#执行文件同步
def rsync_file():
    if not os.path.exists(CLUSTER_DIR):
        sys.exit("集群配置在git中不存在")

    for i in ip_list:
        (s, r) = commands.getstatusoutput("rsync -rltgo %s %s:/" % (CLUSTER_DIR, i))
        # print i, "is ok"
        if s:
            print r

if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.exit("error:请输入一个集群名称参数")

    CLUSTER_NAME = sys.argv[1]
    GIT_DIR = '/job/git/hbase/'
    RSYNC_LOG = '/job/log/RSYNC.log'
    CLUSTER_DIR = GIT_DIR + CLUSTER_NAME + '/'
    NOW = datetime.datetime.now()
    CHECK_TIME = NOW.strftime("%Y-%m-%d#%H:%M")
    M_TIME = NOW.strftime("%Y%m%d%H%M")
    os.system('cd %s && git pull &> /dev/null' % GIT_DIR)
    if len(sys.argv) > 2:
        os.system('find %s | xargs touch -c -m -t %s' % (CLUSTER_DIR, M_TIME))
    FILE_LIST = os.listdir(CLUSTER_DIR)
    if 'etc' in FILE_LIST:
        FILE_LIST.remove('etc')
    # print FILE_LIST, ' '.join(FILE_LIST)
    (s,r) = commands.getstatusoutput('cd %s && chown -R hadp:hadp %s' % (CLUSTER_DIR, ' '.join(FILE_LIST)))
    if s:
        sys.exit("文件属主修改失败")

    # os.system('echo "%s: %s 开始同步----------------------------" >> %s' % (CLUSTER_NAME, CHECK_TIME, RSYNC_LOG))
    ip_list_all = get_ip(CLUSTER_NAME)
    ip_no_list = []
    ip_list = list(set(ip_list_all).difference(set(ip_no_list)))
    if not ip_list:
        sys.exit("ip列表为空")
    # ip_list = ['192.168.146.132', '192.168.146.171']
    rsync_file()
    # os.system('echo "%s: %s 同步结束----------------------------" >> %s' % (CLUSTER_NAME, CHECK_TIME, RSYNC_LOG))
    print "同步完成"

    



    
