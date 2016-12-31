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

def get_tag_id(CLUSTER_NAME):
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
    return tag_id


def get_ip(CLUSTER_NAME,tag_id):

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

def get_rsip_bymem(tag_id,mem_id):
    ip_url = 'http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=19,50,%s,%s&appKey=123456&erp=wangdelong5' % (tag_id,mem_id)
    page = urllib.urlopen(ip_url)
    data = json.load(page)
    dataList = data['data']['dataList']
    rs_ip_list = []
    for i in range(0,len(dataList)):
        rs_ip_list.append(dataList[i]['ip'])
    return rs_ip_list

#执行文件同步
def rsync_file():
    if not os.path.exists(CLUSTER_DIR):
        sys.exit("集群配置在git中不存在")

    for i in ip_list:
        (s, r) = commands.getstatusoutput("rsync -rltgo %s %s:/" % (CLUSTER_DIR, i))
        # print i, "is ok"
        if s:
            print r
#个性化配置同步
def rsync_special_file(rs_ip_list,hbase_version,mem_conf):
    SPECIAL_DIR = GIT_DIR + '_public/' + CLUSTER_NAME + '/' + mem_conf + '/conf/'
    if not os.path.exists(SPECIAL_DIR):
        sys.exit('%s配置在git中不存在' %SPECIAL_DIR)
    for i in rs_ip_list:
        (s,r) = commands.getstatusoutput('rsync -rltgo %s %s:/software/servers/%s/conf' %(SPECIAL_DIR,i,hbase_version))
        if s:
            print r

def get_version():
    bashrc_file = '/job/git/hbase/' + CLUSTER_NAME + '/home/hadp/.bashrc'
    if not os.path.exists(bashrc_file):
        sys.exit("bashrc文件不存在")
    hbase_v = "awk -F '/' '/\/software\/servers\/hbase/{print $NF}' %s" % bashrc_file
    (s,hbase_version) = commands.getstatusoutput(hbase_v)
    if s:
        sys.exit("bashrc安装版本获取失败")
    return hbase_version

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
    (s1,r1) = commands.getstatusoutput('chown -R hadp:hadp /job/git/hbase/_public')
    if s1:
        sys.exit('文件属主修改失败')
    # os.system('echo "%s: %s 开始同步----------------------------" >> %s' % (CLUSTER_NAME, CHECK_TIME, RSYNC_LOG))
    tag_id = get_tag_id(CLUSTER_NAME)
    ip_list_all = get_ip(CLUSTER_NAME,tag_id)
    ip_no_list = []
    ip_list = list(set(ip_list_all).difference(set(ip_no_list)))
    if not ip_list:
        sys.exit("ip列表为空")
    # ip_list = ['192.168.146.132', '192.168.146.171']
    rsync_file()
    # os.system('echo "%s: %s 同步结束----------------------------" >> %s' % (CLUSTER_NAME, CHECK_TIME, RSYNC_LOG))
    hbase_version = get_version()
    
    ip_32_list = get_rsip_bymem(tag_id,'345')
    if ip_32_list:
        rsync_special_file(ip_32_list,hbase_version,'mem_32g')
    ip_64_list = get_rsip_bymem(tag_id,'346')
    if ip_64_list:
        rsync_special_file(ip_64_list,hbase_version,'mem_64g')
    ip_128_list = get_rsip_bymem(tag_id,'347')
    if ip_128_list:
        rsync_special_file(ip_128_list,hbase_version,'mem_128g')
    ip_256_list = get_rsip_bymem(tag_id,'348')
    if ip_256_list:
        rsync_special_file(ip_256_list,hbase_version,'mem_256g')
 
    print "配置同步完成"
