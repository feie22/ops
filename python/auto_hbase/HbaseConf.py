#!/usr/bin/python
#coding:utf-8
#!/bin/usr/python
#coding: utf-8
#===============================================================================
#         FILE: setup.py
#  DESCRIPTION: 客户端调度接口
#       AUTHOR: anbaoyong
#      VERSION: 1.0
#      CREATED: 2015-12-02
#功能：通过集群的id自动生成zk，hadoop，hbase的配置
#描述：此模块编写仓促，没用变量的形式，后续可以升级
#      适应hadoop-2.6.1,hbase-1.1.2 
#===============================================================================
import os
import random
import stat
import urllib,urllib2
import json
import re
import sys
import socket
import commands
import netsnmp
reload(sys)
sys.setdefaultencoding("utf-8")
##服务器管理获取数据
ret = {"result": "NONE", "details": "NONE"}
def _cmd(arg):
    (status, output) = commands.getstatusoutput(arg)
    if status:
   #     res = 'False:%s%s:::%s' % (arg,output,res)
        ret['result'] = False
        ret['details'] = output
        return ret
    else:
        ret['result'] = True
        ret['details'] = output
    #    res = 'True:%s%s:::%s' % (arg,output,res)
        return ret
def get_ip_rack(url):
    '''
        获取ip和机架信息，返回{ip:rack}字典
    '''
    ip_rack_dic = {}
    req = urllib2.Request(url)
    res = urllib2.urlopen(req).read()
    all_data = json.loads(res)
    detail_data = all_data['data']['dataList']
    for ip_rack in detail_data:
        rack_num = ''.join(re.findall(r"\d+",ip_rack['cabinet']))
        if rack_num == '':
            print u"IP:%s,无机架信息！" % ip_rack['ip']
#            sys.exit(1)
        ip_rack_dic[ip_rack['ip']] = "/rack/rack" + rack_num
    return ip_rack_dic
def get_list(url):
    '''
        从服务器管理上获取 ip，并生成有序list
    '''
    return sorted(get_ip_rack(url).keys()) 
def get_local_ip():
    '''
        获取本地ip，返回ip
    '''
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except Exception,e:
        print e 
        return e
    return ip

def get_hostname(url):
    '''
        返回主机名
    '''
    hostname = []
    for ip in get_list(url):
        try:
            hostname.append(netsnmp.snmpwalk('sysName',Version = 2,DestHost = ip,Community = '360buy')[0])
        except Exception,e:
            print e
            print u"IP:%s,获取主机名失败！"  % ip
   #         sys.exit(2)
    return hostname

def write_file(path,hostname_list):
    '''
        接收路径和list
    '''
    with open(path,'w') as f:
        for all_host in hostname_list:
            f.write('%s\n' % all_host)
    
def zk_conf(clusterId):
    '''
        修改zoo.cfg，修改myid，并且启动zk
    '''
    zk_url = 'http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=%s,10&appKey=123456&erp=anbaoyong' % clusterId
    local_ip = get_local_ip()
    conf_path = '/software/servers/zookeeper-3.4.5/conf/zoo.cfg'
    _cmd("sed -i '/2888:3888/d' %s" % conf_path)
    num = 1
    with open(conf_path,'a') as f:
        for ip in get_list(zk_url):
            conf = "server.%d=%s:2888:3888" % (num,ip)
            f.write('%s\n' % conf)
            if ip == local_ip:
                myid = num
            num += 1
    _cmd('mkdir -p /data0/zookeeper-3.4.5/data/')
    _cmd('echo %d >/data0/zookeeper-3.4.5/data/myid' % myid)
    _cmd("sed -i '/export/d' /home/hadp/.bashrc")
    _cmd("echo 'export JAVA_HOME=/software/servers/jdk1.7.0_67' >>/home/hadp/.bashrc")
    _cmd("echo 'export HADOOP_HOME=/software/servers/hadoop-2.6.1' >>/home/hadp/.bashrc")
    _cmd("echo 'export HBASE_HOME=/software/servers/hbase-1.1.2' >>/home/hadp/.bashrc")
    _cmd("echo 'export PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$JAVA_HOME/bin:$HBASE_HOME/bin:$PATH' >>/home/hadp/.bashrc")
    _cmd('chown hadp:hadp -R /data0')
    return _cmd("su - hadp -c '/software/servers/zookeeper-3.4.5/bin/zkServer.sh start'")
    

def hadoop_conf(clustername,clusterId):
    '''
        适应hadoop-2.6.1,hbase-1.1.2,三台jn,一台rm
        修改hdfs-site,yarn-site,core-site，slaves,/etc/hosts,hosts/{datanode,maprednode}
    '''
    nn_url = 'http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=%s,5&appKey=123456&erp=anbaoyong'  % clusterId
    #rm_url = 'http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=%s,6&appKey=123456&erp=anbaoyong'  % clusterId
    jn_url = 'http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=%s,9&appKey=123456&erp=anbaoyong'  % clusterId
    zk_url = 'http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=%s,10&appKey=123456&erp=anbaoyong'  % clusterId
    dn_url = 'http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=%s,7&appKey=123456&erp=anbaoyong'  % clusterId
    cluster_url = 'http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=%s&appKey=123456&erp=anbaoyong'  % clusterId
    nn_hostname_list =  get_hostname(nn_url) 
    #rm_hostname_list = get_hostname(rm_url)
    jn_hostname_list = get_hostname(jn_url)
    zk_hostname_list = get_hostname(zk_url)
    dn_hostname_list = get_hostname(dn_url)
    cluster_hostname_list = get_hostname(cluster_url)   
    ##修改hdfs-site,jn
    jn_node_str = ''
    for jn_node in jn_hostname_list:
        jn_node_str += '%s:8485;' % jn_node
    jn_node_str = jn_node_str[:-1]
    qjournal = "qjournal:\/\/%s\/%s" % (jn_node_str,clustername)
    #qjournal = "qjournal:\/\/%s:8485;%s:8485;%s:8485\/%s" % (jn_hostname_list[0],jn_hostname_list[1],jn_hostname_list[2],clustername)
    #print qjournal
    _cmd("sed -i 's/CLUSTERNAME/%s/g' /software/servers/hadoop-2.6.1/etc/hadoop/hdfs-site.xml" % clustername)
    _cmd("sed -i 's/NAMENODE1/%s/g' /software/servers/hadoop-2.6.1/etc/hadoop/hdfs-site.xml" % nn_hostname_list[0])
    _cmd("sed -i 's/NAMENODE2/%s/g' /software/servers/hadoop-2.6.1/etc/hadoop/hdfs-site.xml" % nn_hostname_list[1])
    _cmd("sed -i 's/JOURNALNODE/%s/g' /software/servers/hadoop-2.6.1/etc/hadoop/hdfs-site.xml" % qjournal)
    ##修改core-site,zk
    zk_node_str = ''
    for zk_node in zk_hostname_list:
        zk_node_str += '%s:2181,' %  zk_node
    zk_node_str = zk_node_str[:-1]
    _cmd("sed -i 's/CLUSTERNAME/%s/g' /software/servers/hadoop-2.6.1/etc/hadoop/core-site.xml" % clustername)
    _cmd("sed -i 's/ZOOKEEPER/%s/g' /software/servers/hadoop-2.6.1/etc/hadoop/core-site.xml" % zk_node_str)
    ###修改yarn-stie,RESOURCEMANAGER
    #_cmd("sed -i 's/RESOURCEMANAGER/%s/g' /software/servers/hadoop-2.6.1/etc/hadoop/yarn-site.xml" % rm_hostname_list[0])
    ##修改slaves，datanode_hosts ， mapred_hosts
    slaves_path = '/software/servers/hadoop-2.6.1/etc/hadoop/slaves'
    datahost_path = '/software/servers/hadoop-2.6.1/etc/hadoop/hosts/datanode_hosts'
    maphost_path = '/software/servers/hadoop-2.6.1/etc/hadoop/hosts/mapred_hosts'
    write_file(slaves_path,dn_hostname_list)
    write_file(datahost_path,dn_hostname_list)
    write_file(maphost_path,dn_hostname_list)
    #修改/etc/hosts
    cluster_ip_hostname_list = []
    num = 0
    cluster_ip_list = get_list(cluster_url)
    if len(cluster_ip_list) == len(cluster_hostname_list):
        while num < len(cluster_ip_list):
            cluster_ip_hostname_list.append(cluster_ip_list[num] + ' '+ cluster_hostname_list[num])
            num += 1
        write_file('/etc/hosts',cluster_ip_hostname_list)
    else:
        ret['result'] = False
        ret['details'] = 'error: /etc/hosts'
        return ret

        
    ####hbase
    #修改hbase-site
    _cmd("sed -i 's/CLUSTERNAME/%s/g' /software/servers/hbase-1.1.2/conf/hbase-site.xml" % clustername)
    _cmd("sed -i 's/ZOOKEEPER/%s/g' /software/servers/hbase-1.1.2/conf/hbase-site.xml" % zk_node_str)
    # 修改regionservers
    region_path = '/software/servers/hbase-1.1.2/conf/regionservers'
    write_file(region_path,dn_hostname_list)
    #修改backup-masters
    back_path = '/software/servers/hbase-1.1.2/conf/backup-masters'
    write_file(back_path,[nn_hostname_list[1]])
    ##copy hadoop配置到hbase
    _cmd('cp /software/servers/hadoop-2.6.1/etc/hadoop/core-site.xml /software/servers/hbase-1.1.2/conf/')
    _cmd('cp /software/servers/hadoop-2.6.1/etc/hadoop/hdfs-site.xml /software/servers/hbase-1.1.2/conf/')
    _cmd('chmod 755 /data* && chown hadp:hadp -R /data*')
    ##配置bashrc
    _cmd("sed -i '/export/d' /home/hadp/.bashrc")
    _cmd("echo 'export JAVA_HOME=/software/servers/jdk1.7.0_67' >>/home/hadp/.bashrc")
    _cmd("echo 'export HADOOP_HOME=/software/servers/hadoop-2.6.1' >>/home/hadp/.bashrc")
    _cmd("echo 'export HBASE_HOME=/software/servers/hbase-1.1.2' >>/home/hadp/.bashrc")
    return  _cmd("echo 'export PATH=$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$JAVA_HOME/bin:$HBASE_HOME/bin:$PATH' >>/home/hadp/.bashrc")

#hadoop_conf('aby_test','449')











