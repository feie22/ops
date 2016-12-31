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

if len(sys.argv) ==1:
    print "error:请输入一个集群名称参数"
    sys.exit()
CLUSTER_NAME = sys.argv[1]

if not os.path.exists('/tmp/%s' % CLUSTER_NAME):
    print "info:创建集群日志目录"
    os.system('mkdir /tmp/%s' %CLUSTER_NAME)

CLIENT = salt.client.LocalClient()

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
    ip_s2 = ','.join(ip_list2)

    return ip_s2

#执行文件一致性检查
def check_md5():
    ip_str = get_ip(CLUSTER_NAME)
    ip_list = ip_str.split(',')
    # ip_list = ['172.17.38.217', '172.17.38.216']
    md5_dic = {}
    base_conf = ['/etc/sysctl.conf', '/etc/security/limits.conf', '/etc/resolv.conf', '/home/hadp/.bashrc', '/etc/hosts']
    hadp_conf = ['/etc/hadoop/core-site.xml', '/etc/hadoop/hdfs-site.xml', '/etc/hadoop/mapred-site.xml', '/etc/hadoop/yarn-site.xml', '/etc/hadoop/hadoop-env.sh', '/etc/hadoop/mapred-env.sh', '/etc/hadoop/yarn-env.sh', '/etc/hadoop/hadoop-policy.xml', '/etc/hadoop/hosts/datanode_hosts', '/etc/hadoop/hosts/mapred_hosts', '/etc/hadoop/hosts/exclude_datanode_hosts', '/etc/hadoop/hosts/exclude_mapred_hosts', '/etc/hadoop/slaves', '/etc/hadoop/rack.data']
    hbase_conf =['/conf/backup-masters', '/conf/core-site.xml', '/conf/hbase-env.sh', '/conf/hbase-policy.xml', '/conf/hbase-site.xml', '/conf/hdfs-site.xml', '/conf/regionservers']

    os.system('cd %s && git pull > /dev/null' % GIT_DIR)

    hdap_pre = commands.getoutput("awk -F'=' '/HADOOP_HOME=/{print $2}' %s%s/home/hadp/.bashrc" % (GIT_DIR, CLUSTER_NAME))
    hbase_pre = commands.getoutput("awk -F'=' '/HBASE_HOME=/{print $2}' %s%s/home/hadp/.bashrc" % (GIT_DIR, CLUSTER_NAME))

    for i in range(0,len(hadp_conf)):
        hadp_conf[i]= hdap_pre + hadp_conf[i]
    for i in range(0,len(hbase_conf)):
        hbase_conf[i]= hbase_pre + hbase_conf[i]

    base_conf.extend(hadp_conf)
    base_conf.extend(hbase_conf)

    for i in base_conf:#将md5校验值加入字典
        (s, r)=commands.getstatusoutput("md5sum %s%s%s | awk '{print $1}'" % (GIT_DIR, CLUSTER_NAME, i))
        md5_dic[i] = r

    os.system('rm -f /tmp/%s/md5.log' % CLUSTER_NAME)
    os.system('touch /tmp/%s/md5.log' % CLUSTER_NAME)

    for n in md5_dic.iterkeys():
        cmd = "md5sum " + n + " | awk '{print $1}' "
        ret_dic = CLIENT.cmd(ip_list, 'cmd.run', [cmd], expr_form='list')
        for i in ip_list:
            if ret_dic[i] != md5_dic[n]:
                os.system("echo '%s %s' >> /tmp/%s/md5.log" % (i, n, CLUSTER_NAME ))
                # print "server is %s, server_md5 is %s, source_md5 is %s " % (i, ret_dic[i], md5_dic[n])
    (s, r) = commands.getstatusoutput("cat /tmp/%s/md5.log | wc -l" % CLUSTER_NAME)
    if int(r):
        print "error:个别服务器配置文件不一致或个别服务器返回异常（/tmp/%s/md5.log）" % CLUSTER_NAME
    else:
        print "info:配置文件一致性检查正常"
        os.system('rm -rf /tmp/%s/md5.log' % CLUSTER_NAME)


def check_service():

    print "info:开始检查所有节点的基础服务状态（crond snmpd gmond sshd rsyslog sysstat）"
    ip_list = get_ip(CLUSTER_NAME)
    cmd_log = '''salt -L %s cmd.run 'for i in crond snmpd gmond sshd rsyslog sysstat; do service $i status; done |egrep -v "salt-minion|pid" '  > /tmp/%s/service.log''' % (ip_list, CLUSTER_NAME)
    (s1, r1) = commands.getstatusoutput(cmd_log)
    cmd_resault = "cat /tmp/%s/service.log|egrep -v '172|Minions' |wc -l" % CLUSTER_NAME
    (s2, r2) = commands.getstatusoutput(cmd_resault)
    if int(r2) > 0:
        print "error:个别基础服务未安装(未运行)或个别服务器返回异常（/tmp/%s/service.log）" % CLUSTER_NAME
    else:
        print "info:基础服务状态正常"
        os.system('rm -rf /tmp/%s/service.log' % CLUSTER_NAME)

#执行文件错误检查

def check_messages():
    print "info:开始检查所有节点系统日志messages文件"
    ip_list = get_ip(CLUSTER_NAME)
    cmd_log = '''salt -L %s cmd.run 'cat /var/log/messages |grep -E "fail|error"|grep -v salt-minion'  > /tmp/%s/messages.log''' % (ip_list, CLUSTER_NAME)
    (s1, r1) = commands.getstatusoutput(cmd_log)
    cmd_resault = "cat /tmp/%s/messages.log|grep -v 172 | grep -v Minions|wc -l" % CLUSTER_NAME
    (s2, r2) = commands.getstatusoutput(cmd_resault)
    if int(r2) > 1:
        print "error:系统日志messages有报错信息或个别服务器返回异常（/tmp/%s/message.log）" % CLUSTER_NAME
    else:
        print "info:系统日志messages文件正常"
        os.system('rm -rf /tmp/%s/messages.log' % CLUSTER_NAME)

def check_dmesg():
    print "info:开始检查所有节点系统日志dmesg文件"
    ip_list = get_ip(CLUSTER_NAME)
    cmd_log = '''salt -L %s cmd.run 'dmesg |grep -E "Error|error" ' > /tmp/%s/dmesg.log ''' %(ip_list, CLUSTER_NAME)
    (s1, r1) = commands.getstatusoutput(cmd_log)
    cmd_resault = '''cat /tmp/%s/dmesg.log|grep -v "failed with error -22"| \grep -v "ERST: Error Record"| grep -v "ACPI Error:"|grep -v 172|grep -v Minions|wc -l''' % CLUSTER_NAME
    (s2, r2) = commands.getstatusoutput(cmd_resault)
    if int(r2) > 1:
        print "error:系统日志dmesg有报错信息或个别服务器返回异常（/tmp/%s/dmesg.log）" % CLUSTER_NAME
    else:
        print "info:系统日志dmesg文件正常"
        os.system('rm -rf /tmp/%s/dmesg.log' % CLUSTER_NAME)

def check_loadavg():
    print "info:开始检查所有节点的平均负载"
    ip_list = get_ip(CLUSTER_NAME)
    cmd_log = '''salt -L %s cmd.run "uptime|awk -F'average: ' '{print \$2}'| awk -F',' '{if (\$1 >50 && \$2 >50 && \$3 >50){print \$1,\$2,\$3} else {print 1}}'" > /tmp/%s/load.log''' % (ip_list, CLUSTER_NAME)
    (s1, r1) = commands.getstatusoutput(cmd_log)
    cmd_resault = '''cat /tmp/%s/load.log|grep -v 172|sort|uniq|wc -l''' % CLUSTER_NAME
    (s2, r2) = commands.getstatusoutput(cmd_resault)
    if int(r2) > 1:
        print "error:个别服务器平均负载异常或个别服务器返回异常（/tmp/%s/load.log）" % CLUSTER_NAME
    else:
        print "info:所有节点负载正常"
        os.system('rm -rf /tmp/%s/load.log' % CLUSTER_NAME)

def check_disk_use():
    print "info:开始检查所有节点的磁盘使用率"
    ip_list = get_ip(CLUSTER_NAME)
    cmd_p1 = '''df -h|grep -E 'data*|/'|awk '{print \"dir:\"\$6 \" tused:\"\$5}'|grep -E '172.|([9][5-9]|100)%' '''
    cmd_log = ''' salt -L %s cmd.run "%s" > /tmp/%s/disk.log ''' % (ip_list, cmd_p1, CLUSTER_NAME)
    (s1, r1) = commands.getstatusoutput(cmd_log)
    cmd_resault = '''cat /tmp/%s/disk.log|grep -v 172|sort|uniq|wc -l''' % CLUSTER_NAME
    (s2, r2) = commands.getstatusoutput(cmd_resault)
    if int(r2) > 0:
        print "error:个别服务器磁盘使用率异常或个别服务器返回异常\n以下为明细"
        os.system("grep dir  /tmp/$CLUSTER_NAME/disk.log  -B 1|grep -v '\-\-'")
    else:
        print "info:所有节点磁盘使用率正常"
        os.system('rm -rf /tmp/%s/disk.log' % CLUSTER_NAME)

def check_inode_use():
    print "info:开始检查所有节点的磁盘inode使用率"
    ip_list = get_ip(CLUSTER_NAME)
    cmd_p1 = ''' df -i|grep -E 'data*|/'$|awk '{print \"dir:\"\$6 \" tused:\"\$5}'|grep -E '172.|([7-9][0-9]|100)%$' '''
    cmd_log = '''salt -L %s cmd.run "" > /tmp/%s/disk_inode.log''' % (ip_list, CLUSTER_NAME)
    (s1, r1) = commands.getstatusoutput(cmd_log)
    cmd_resault = '''cat /tmp/%s/disk_inode.log|grep -v 172|sort|uniq|wc -l''' % CLUSTER_NAME
    (s2, r2) = commands.getstatusoutput(cmd_resault)
    if int(r2) > 0:
        print "error:个别服务器磁盘inode使用率异常或个别服务器返回异常（/tmp/%s/disn_inode.log）" % CLUSTER_NAME
    else:
        print "info:所有节点磁盘inode使用率正常"
        os.system('rm -rf /tmp/%s/disk_inode.log' % CLUSTER_NAME)

def check_mem_use():
    print "info:开始检查所有节点的内存使用率"
    ip_list = get_ip(CLUSTER_NAME)
    cmd_log = '''salt -L %s cmd.run "free -m|grep "Mem"|awk '{if ((\$3-\$7-\$6)/\$2 > 0.9) {print 0}}'" > /tmp/%s/mem.log''' % (ip_list, CLUSTER_NAME)
    (s1, r1) = commands.getstatusoutput(cmd_log)
    cmd_resault = '''cat /tmp/%s/mem.log|grep -v 172|sort|uniq|wc -l''' % CLUSTER_NAME
    (s2, r2) = commands.getstatusoutput(cmd_resault)
    if int(r2) > 0:
        print "error:个别服务器内存使用率异常或个别服务器返回异常（/tmp/%s/mem.log）" % CLUSTER_NAME
    else:
        print "info:所有节点内存使用率正常"
        os.system('rm -rf /tmp/%s/mem.log' % CLUSTER_NAME)

def check_swap_use():
    print "info:开始检查所有节点的swap使用率"
    ip_list = get_ip(CLUSTER_NAME)
    cmd_log = '''salt -L %s cmd.run "free -m|grep "Swap"|awk '{if (\$3/\$2 > 0.2) {print 0}}'" > /tmp/%s/swap.log''' % (ip_list, CLUSTER_NAME)
    (s1, r1) = commands.getstatusoutput(cmd_log)
    cmd_resault = '''cat /tmp/%s/swap.log|grep -v 172|sort|uniq|wc -l''' % CLUSTER_NAME
    (s2, r2) = commands.getstatusoutput(cmd_resault)
    if int(r2) > 0:
        print "error:个别服务器swap使用率异常或个别服务器返回异常（/tmp/%s/swap.log）" % CLUSTER_NAME
    else:
        print "info:所有节点swap使用率正常"
        os.system('rm -rf /tmp/%s/swap.log' % CLUSTER_NAME)

def check_bandwidth():
    print "info:开始检查所有节点的网卡带宽制式"
    ip_list = get_ip(CLUSTER_NAME)
    cmd_log = '''salt -L %s cmd.run "ethtool \`ifconfig |grep {{ grains.id }} -B 1 |head -1|awk  '{print \$1} '\` " template=jinja > /tmp/%s/ethtool.log''' % (ip_list, CLUSTER_NAME)
    (s1, r1) = commands.getstatusoutput(cmd_log)
    cmd_resault = '''cat /tmp/%s/ethtool.log|grep Speed|awk -F ':' '{print $2}'|awk -F 'M' '{if ($1 < 1000) {print 0}}'|grep -v 172|sort|uniq|wc -l''' % CLUSTER_NAME
    (s2, r2) = commands.getstatusoutput(cmd_resault)
    if int(r2) > 0:
        print "error:个别服务器网卡带宽制式异常或个别服务器返回异常（/tmp/%s/ethtool.log）" % CLUSTER_NAME
    else:
        print "info:所有节点网卡制式正常"
        os.system('rm -rf /tmp/%s/ethtool.log' % CLUSTER_NAME)

def check_connect():
    print "info:开始检查所有节点的连接数"
    ip_list = get_ip(CLUSTER_NAME)
    cmd_log = '''salt -L %s cmd.run "netstat -ant|wc -l|awk '{if (\$1 > 30000) {print 0}}'" > /tmp/%s/netstat.log''' % (ip_list, CLUSTER_NAME)
    (s1, r1) = commands.getstatusoutput(cmd_log)
    cmd_resault = '''cat /tmp/%s/netstat.log|grep -v 172|sort|uniq|wc -l''' % CLUSTER_NAME
    (s2, r2) = commands.getstatusoutput(cmd_resault)
    if int(r2) > 0:
        print "error:个别服务器连接数超过3w异常或返回异常（/tmp/%s/netstat.log）" % CLUSTER_NAME
    else:
        print "info:所有节点连接数正常"
        os.system('rm -rf /tmp/%s/netstat.log' % CLUSTER_NAME)

def check_zombie():
    print "info:开始检查所有节点的僵尸进程"
    ip_list = get_ip(CLUSTER_NAME)
    cmd_log = '''salt -L %s cmd.run 'ps -ef|grep defunct|grep -v grep|wc -l' > /tmp/%s/zombie.log''' % (ip_list, CLUSTER_NAME)
    (s1, r1) = commands.getstatusoutput(cmd_log)
    cmd_resault = '''cat /tmp/%s/zombie.log|grep -v 172|sort|uniq|wc -l''' % CLUSTER_NAME
    (s2, r2) = commands.getstatusoutput(cmd_resault)
    if int(r2) > 1:
        print "error:个别服务器存在僵尸进程或返回异常（/tmp/%s/zombie.log）" % CLUSTER_NAME
    else:
        print "info:所有节点不存在僵尸进程"
        os.system('rm -rf /tmp/%s/zombie.log' % CLUSTER_NAME)

def check_bad_disk():
    print "info:开始检查所有节点是否存在坏盘"
    ip_list = get_ip(CLUSTER_NAME)
    cmd_log1 = '''salt -L %s cmd.run 'ls / | grep -e "^data[0-9]"|xargs -i touch /{}/diskcheck' runas=hadp > /tmp/%s/diskcheck.log''' % (ip_list, CLUSTER_NAME)
    cmd_log2 = '''salt -L %s cmd.run 'ls / | grep -e "^data[0-9]"|xargs -i rm /{}/diskcheck' >> /tmp/$CLUSTER_NAME/diskcheck.log'''
    (s1, r1) = commands.getstatusoutput(cmd_log1)
    (s2, r2) = commands.getstatusoutput(cmd_log2)
    cmd_resault1 = '''cat /tmp/%s/diskcheck.log|grep -v 172|sort|uniq|wc -l''' % CLUSTER_NAME
    (s3, r3) = commands.getstatusoutput(cmd_resault1)
    if int(r3) > 0:
        print "error:个别服务器存在坏盘或返回异常（/tmp/%s/diskcheck.log）" % CLUSTER_NAME
    else:
        print "info:所有节点不存在坏盘"
        os.system('rm -rf /tmp/%s/diskcheck.log' % CLUSTER_NAME)

    print "info:开始检查所有节点是否存在掉盘"
    cmd_log3 = '''salt -L %s cmd.run 'if [ `grep data /etc/fstab|grep -v "#"|wc -l` -gt `df -h|grep data|wc -l` ];  then echo 0; fi' > /tmp/%s/diskcheck1.log''' % (ip_list, CLUSTER_NAME)
    (s4, r4) = commands.getstatusoutput(cmd_log3)
    cmd_resault2 = '''cat /tmp/%s/diskcheck1.log|grep -v 172|sort|uniq|wc -l''' % CLUSTER_NAME
    (s5, r5) = commands.getstatusoutput(cmd_resault2)
    if int(r5) > 0:
        print "error:个别服务器存在掉盘或返回异常（/tmp/%s/diskcheck1.log）" % CLUSTER_NAME
    else:
        print "info:所有节点不存在掉盘"
        os.system('rm -rf /tmp/%s/diskcheck1.log' % CLUSTER_NAME)


if __name__ == '__main__':
    check_md5()
    # check_service()
    # check_messages()
    # check_dmesg()
    # check_loadavg()
    # check_disk_use()
    # check_inode_use()
    # check_swap_use()
    # check_bandwidth()
    # check_connect()
    # check_zombie()
    # check_bad_disk()
    # ip_list = get_ip(CLUSTER_NAME)
    # print ip_list