#!/usr/bin/python
#coding:utf-8

"""
@description: 集群初始化
@author: wangdelong@jd.com
@createtime: 2016/8/11 0006
@updatetime: ?
"""

import urllib
import json
import re
import sys
import os
import saltapi
import commands
import time
import hbase

reload(sys)
sys.setdefaultencoding('utf-8')

if len(sys.argv) < 3:
    sys.exit("请输入hadoop/hbase集群名称及上线id")
HADOOP_NAME = sys.argv[1]
HBASE_NAME = sys.argv[1]
ID = sys.argv[2]
GIT_DIR = '/job/git/hbase/'
BASE_DIR = '/job/ops/'
LOG_FILE = BASE_DIR + "exec.log"
# SALT_GIT_DIR = "/etc/salt/srv/salt/git/hbase"
# SALT_IP = "172.19.185.84"   # 与本机打通ssh信任
DNS_IP = "172.22.213.58"    # 与本机打通ssh信任


# 写日志及配置文件
def write_file(file, content, w_mode='a'):
    if file == LOG_FILE:
        print content,
    try:
        f = open(file, w_mode)
        f.write(content)
    except:
        sys.exit("%s文件写入失败，写入内容：%s" % (file, content))
    finally:
        f.close()

# 生成saltapi接口参数
def create_params(fun,ip_list,*args):
    num = 1
    params = {
        'tgt': ','.join(ip_list),
        'fun': fun
        }
    if len(args) != 0:
        for arg in args:
            params['arg'+str(num)] = arg
            num += 1
   # print params
    return params


# 通过bashrc获取hadoop、hbas、jdk版本
def get_version():
    bashrc_file = GIT_DIR + HADOOP_NAME + "/home/hadp/.bashrc"
    if not os.path.exists(bashrc_file):
        sys.exit("bashrc文件不存在")
    cmd_jdk = "awk -F '/' '/\/software\/servers\/jdk/{print $NF}' %s" % bashrc_file
    cmd_hadoop = "awk -F '/' '/\/software\/servers\/hadoop/{print $NF}' %s" % bashrc_file
    cmd_hbase = "awk -F '/' '/\/software\/servers\/hbase/{print $NF}' %s" % bashrc_file
    (s1, jdk_v) = commands.getstatusoutput(cmd_jdk)
    (s2, hadoop_v) = commands.getstatusoutput(cmd_hadoop)
    (s3, hbase_v) = commands.getstatusoutput(cmd_hbase)
    if s1 or s2 or s3:
        sys.exit("bashrc安装版本获取失败")
    version_dic = {'jdk_v':jdk_v, 'hadoop_v':hadoop_v, 'hbase_v':hbase_v}
    return version_dic

# 获取集群ip列表的字典，及ip--机架信息的字典
def get_ip():
    # 根据集群名称，获取tag_id
    url_tag_api = "http://bdp.jd.com/ops/api/server/findAllTags.ajax?tagType=2&appKey=123456&erp=wangdelong5"
    time.sleep(0.05)
    page1 = urllib.urlopen(url_tag_api)
    data1 = json.load(page1)
    data_list1 = data1['data']['dataList']
    hadoop_id = ''
    hbase_id = ''
    for i in range(0, len(data_list1)):
        if data_list1[i]['name'] == HADOOP_NAME:
            hadoop_id = data_list1[i]['id']

    if not hadoop_id:
        sys.exit("集群%s id获取失败，BDP中无此集群" % HADOOP_NAME)
    hbase_id = hadoop_id
    print "tag haddop %s hbase %s" % (hadoop_id, hbase_id)

    # 根据tag_id获取集群的ip角色的字典
    hadoop_tag_dic = {'NN':5, 'ZK':10, 'ALL':''}
    hbase_tag_dic = {'DN':7,'HM':71, 'ALL':''}
    hadoop_ip_dic = {}
    hbase_ip_dic = {}
    hbase_rack_dic = {}

    for m, n in hadoop_tag_dic.iteritems():
        url_ip_api = "http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=19,%s,%s&appKey=123456&erp=wangdelong5" % (hadoop_id, n)
        time.sleep(0.1)
        page = urllib.urlopen(url_ip_api)
        data = json.load(page)
        data_list = data['data']['dataList']
        hadoop_ip_dic[m] = []
        for i in range(0, len(data_list)):
            hadoop_ip_dic[m].append(data_list[i]['ip'])
        # ip_all.extend(ip_dic[j])
        content = "hadoop集群" + HADOOP_NAME + ' ' + m + "：" + str(len(hadoop_ip_dic[m])) + "\n"
        write_file(LOG_FILE, content)
    hadoop_ip_dic['NO_ZK'] = list(set(hadoop_ip_dic['ALL']).difference(set(hadoop_ip_dic['ZK'])))

    for j, k in hbase_tag_dic.iteritems():
        url_ip_api = "http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=19,589,%s,%s&appKey=123456&erp=wangdelong5" % (hbase_id, k)
        time.sleep(0.1)
        page = urllib.urlopen(url_ip_api)
        data = json.load(page)
        data_list = data['data']['dataList']
        hbase_ip_dic[j] = []
        for i in range(0, len(data_list)):
            hbase_ip_dic[j].append(data_list[i]['ip'])
        # ip_all.extend(ip_dic[j])
        content = "hbase集群" + HBASE_NAME + ' ' + j + "：" + str(len(hbase_ip_dic[j])) + "\n"
        write_file(LOG_FILE, content)
        if j == 'DN' and hbase_ip_dic['DN']:
            for ip_rack in data_list:
                rack_num = ''.join(re.findall(r"\d+", ip_rack['cabinet']))
                if not rack_num:
                    content = "IP:%s,无机架信息！\n" % ip_rack['ip']
                    write_file(LOG_FILE, content)
                hbase_rack_dic[ip_rack['ip']] = "/rack/rack" + rack_num

    if not hbase_ip_dic['ALL']:
        sys.exit("集群内无待上线IP")
    # ip_dic['all'] = list(set(ip_all))
    # content = "ALL：" + str(len(ip_dic['all'])) + "\n"
    # write_file(LOG_FILE, content)
    return hadoop_ip_dic, hbase_ip_dic, hbase_rack_dic

def salt_test(ip_list):
    fun = 'test.ping'
    params = create_params(fun, ip_list)
    ret = saltapi.main(params)
    ip_list_alive = ret[0].keys()
    ip_no_alive = list(set(ip_list).difference(set(ip_list_alive)))
    if ip_no_alive:
        sys.exit("部分主机salt无法连通\n%s" % ip_no_alive)
    content = "salt连通性测试完成\n"
    write_file(LOG_FILE, content)

def salt_update(ip_list):
    fun = 'saltutil.sync_modules'
    params = create_params(fun, ip_list)
    ret = saltapi.main(params)
    ip_list_yes = ret[0].keys()
    ip_no = list(set(ip_list).difference(set(ip_list_yes)))
    if ip_no:
        sys.exit("部分主机salt模块同步失败\n%s" % ip_no)
    content = "salt模块同步完成\n"
    write_file(LOG_FILE, content)

def set_dns(ip_list):
    fun = 'grains.item'
    arg = 'localhost'
    params = create_params(fun, ip_list, arg)
    ret = saltapi.main(params)
    ret_dic = ret[0]
    dns_dic = {}
    for k in ret_dic.iterkeys():
        dns_dic[k] = ret_dic[k][arg]
    strtime = time.strftime('%Y%m%d_%H%M', time.localtime())
    domain_file = 'domain_%s.txt' % strtime
    domain_path = BASE_DIR + 'domain/' + domain_file
    content = ''
    for i, n in dns_dic.iteritems():
        content = content + n + ' ' + i + '\n'
    write_file(domain_path, content, 'w')
    cmd = "scp %s %s:/opt/ddns/domain && ssh %s 'ddnstool -a /opt/ddns/domain/%s'" % (domain_path, DNS_IP, DNS_IP, domain_file)
    (s, r) = commands.getstatusoutput(cmd)
    print r
    if s:
        content = "添加DNS失败\n"
        write_file(LOG_FILE, content)
    else:
        content = "添加DNS成功\n"
        write_file(LOG_FILE, content)
    return dns_dic

def set_hadoop_conf(dns_dic, hbase_rack_dic,version_dic):
    etc_hosts = GIT_DIR + HADOOP_NAME + '/etc/hosts'
    content_etc = '##auto_deploy_hbase_%s\n' % ID
    (s, r) = commands.getstatusoutput("grep %s %s" % (ID, etc_hosts))
    if not s:
        return
    for i, n in dns_dic.iteritems():
        content_etc = content_etc + i + '  ' + n + '\n'
    write_file(etc_hosts, content_etc)

    slave_file = GIT_DIR + HADOOP_NAME + '/software/servers/' + version_dic['hadoop_v'] + '/etc/hadoop/slaves'
    dnhost_file = GIT_DIR + HADOOP_NAME + '/software/servers/' + version_dic['hadoop_v'] + '/etc/hadoop/hosts/datanode_hosts'
    mphost_file = GIT_DIR + HADOOP_NAME + '/software/servers/' + version_dic['hadoop_v'] + '/etc/hadoop/hosts/mapred_hosts'
    content_hostname = '##auto_deploy_hbase_%s\n' % ID
    for j in hbase_rack_dic.iterkeys():
        content_hostname = content_hostname + dns_dic[j] + '\n'

    write_file(slave_file, content_hostname)
    write_file(dnhost_file, content_hostname)
    write_file(mphost_file, content_hostname)

    rack_file = GIT_DIR + HADOOP_NAME + '/software/servers/' + version_dic['hadoop_v'] + '/etc/hadoop/rack.data'
    content_rack = '##auto_deploy_hbase_%s\n' % ID
    for m, n in hbase_rack_dic.iteritems():
        content_rack = content_rack + m + ' ' + dns_dic[m] + ' ' + n + '\n'
    write_file(rack_file, content_rack)

def set_hbase_conf(dns_dic, hbase_rack_dic, version_dic, hbase_ip_dic):
    rs_file = GIT_DIR + HBASE_NAME + '/software/servers/' + version_dic['hbase_v'] + '/conf/regionservers'
    content_hostname = '##auto_deploy_hbase_%s\n' % ID
    (s, r) = commands.getstatusoutput("grep %s %s" % (ID, rs_file))
    if not s:
        return
    for j in hbase_rack_dic.iterkeys():
        content_hostname = content_hostname + dns_dic[j] + '\n'
    if hbase_ip_dic['HM']:
        write_file(rs_file, content_hostname, 'w')
        bak_m_file = GIT_DIR + HBASE_NAME + '/software/servers/' + version_dic['hbase_v'] + '/conf/backup-masters'
        write_file(bak_m_file, dns_dic[hbase_ip_dic['HM'][1]], 'w')
    else:
        write_file(rs_file, content_hostname)


def sync_bashrc(ip_list):
    # cmd = "ssh %s 'cd %s && git pull' && chown -R hadp:hadp ." % (SALT_IP, SALT_GIT_DIR)
    # (s, r) = commands.getstatusoutput(cmd)
    # if s:
    #     sys.exit("salt git pull 失败:%s" % r)
    fun = "cp.get_file"
    arg1 = "salt://%s/home/hadp/.bashrc" % HADOOP_NAME
    arg2 = "/home/hadp/.bashrc"
    params = create_params(fun, ip_list, arg1, arg2)
    ret = saltapi.main(params)
    ip_no = []
    for i, n in ret[0].iteritems():
        if not n:
            ip_no.append(i)
    if ip_no:
        # sys.exit("部分主机bashrc同步失败\n%s" % ip_no)
        print "部分主机bashrc同步失败\n%s" % ip_no
    content = "bashrc同步完成\n"
    write_file(LOG_FILE, content)

def sync_ssh(hbase_ip_dic):
    fun = "cmd.run"
    arg1 = "mkdir -p /home/hadp/.ssh"
    params = create_params(fun, hbase_ip_dic['ALL'], arg1)
    ret = saltapi.main(params)
    ip_no = []
    for i, n in ret[0].iteritems():
        if  n:
            ip_no.append(i)
            print n
    if ip_no:
        sys.exit("创建ssh目录失败\n%s" % ip_no)
    if hbase_ip_dic['HM']:
        fun = "cp.get_dir"
        arg1 = "salt://_public/.ssh"
        arg2 = "/home/hadp"
        params = create_params(fun, hbase_ip_dic['HM'], arg1, arg2)
        ret = saltapi.main(params)
        ip_no = []
        for i, n in ret[0].iteritems():
            if not n:
                ip_no.append(i)
        if ip_no:
            sys.exit("HM节点ssh-key同步失败\n%s" % ip_no)
    fun = "cp.get_file"
    arg1 = "salt://_public/.ssh/authorized_keys"
    arg2 = "/home/hadp/.ssh/authorized_keys"
    params = create_params(fun, hbase_ip_dic['ALL'], arg1, arg2)
    ret = saltapi.main(params)
    ip_no = []
    for i, n in ret[0].iteritems():
        if n != "/home/hadp/.ssh/authorized_keys":
            ip_no.append(i)
            print n
    if ip_no:
        sys.exit("部分主机ssh-key同步失败\n%s" % ip_no)

    fun = 'cmd.run'
    arg = "chown -R hadp:hadp /home/hadp/.ssh ; chmod 700 /home/hadp/.ssh"
    params = create_params(fun, hbase_ip_dic['ALL'], arg)
    ret = saltapi.main(params)
    ip_no = []
    for i, n in ret[0].iteritems():
        if n:
            ip_no.append(i)
    if ip_no:
        sys.exit(".ssh目录权限修改失败\n%s" % ip_no)

    content = "ssh-key同步完成\n"
    write_file(LOG_FILE, content)
    # ret_dick = ret[0]

def sync_hbase_conf(hbase_ip_dic):
    fun1 = "cp.get_dir"
    arg1 = "salt://%s/software" % HBASE_NAME
    arg2 = "/"
    params = create_params(fun1, hbase_ip_dic['ALL'], arg1, arg2)
    ret = saltapi.main(params)
    ip_no = []
    for i, n in ret[0].iteritems():
        if not n:
            ip_no.append(i)
        print n
    if ip_no:
        sys.exit("hbase配置同步失败\n%s" % ip_no)

    content = "hbase配置同步完成\n"
    write_file(LOG_FILE, content)

def sync_hadoop_conf(hadoop_ip_dic):
    fun = "cp.get_file"
    arg1 = "salt://%s/etc/hosts" % HADOOP_NAME
    arg2 = "/etc/hosts"
    params = create_params(fun, hadoop_ip_dic['NO_ZK'], arg1, arg2)
    ret = saltapi.main_async(params)
    jid = ret[0]['jid']
    content = "sync_etc_hosts jid：" + jid + '\n'
    write_file(LOG_FILE, content)
    time.sleep(5)
    fun = "cp.get_dir"
    arg1 = "salt://%s/software" % HADOOP_NAME
    arg2 = "/"
    params = create_params(fun, hadoop_ip_dic['NO_ZK'], arg1, arg2)
    ret = saltapi.main_async(params)
    jid = ret[0]['jid']
    content = "sync_hadoop_sofware jid：" + jid + '\n'
    write_file(LOG_FILE, content)
    time.sleep(len(hadoop_ip_dic['NO_ZK']))

    # fun = "cp.get_file"
    # arg1 = "salt://%s/software/servers/%s/etc/hadoop/slaves" % (HADOOP_NAME, version_dic['hadoop_v'])
    # arg2 = "/software/servers/%s/etc/hadoop/slaves" % version_dic['hadoop_v']
    # params = create_params(fun, hadoop_ip_dic['NO_ZK'], arg1, arg2)
    # ret = saltapi.main(params)
    # # ret_dick = ret[0]
    # ip_no = []
    # for i, n in ret[0].iteritems():
    #     if n != arg2:
    #         ip_no.append(i)
    #         print n
    # if ip_no:
    #     sys.exit("hadoop配置同步失败\n%s" % arg2)

    content = "hadoop配置异步同步完成\n"
    write_file(LOG_FILE, content)

def git_push():
    cmd = "cd %s && git commit -a -m 'auto deploy change' && git push origin master " % GIT_DIR
    (s, r) = commands.getstatusoutput(cmd)
    # if s:
    #     content = "Git push失败，程序退出"
    #     write_file(LOG_FILE, content)
    #     print r
    #     sys.exit(1)
    # else:
    content = "Git push完成，延迟60秒\n"
    write_file(LOG_FILE, content)
    time.sleep(61)

def refresh_nodes(hadoop_ip_dic):
    cmd1 = "su - hadp -c 'hadoop dfsadmin -fs hdfs://%s:8020/ -refreshNodes > /dev/null'" % hadoop_ip_dic['NN'][0]
    fun = "cmd.run"
    params = create_params(fun, [hadoop_ip_dic['NN'][0]], cmd1, )
    ret = saltapi.main(params)
    ip_no = []
    for i, n in ret[0].iteritems():
        if not n:
            ip_no.append(i)
        print n
    if ip_no:
        sys.exit("refreshNodes失败\n%s" % [hadoop_ip_dic['NN'][0]])

    cmd2 = "su - hadp -c 'hadoop dfsadmin -fs hdfs://%s:8020/ -refreshNodes > /dev/null'" % hadoop_ip_dic['NN'][1]
    params = create_params(fun, [hadoop_ip_dic['NN'][1]], cmd2)
    ret = saltapi.main(params)
    ip_no = []
    for i, n in ret[0].iteritems():
        if not n:
            ip_no.append(i)
        print n
    if ip_no:
        sys.exit("refreshNodes失败\n%s" % [hadoop_ip_dic['NN'][1]])

    cmd = "su - hadp -c 'hadoop dfsadmin -refreshNodes > /dev/null'"
    params = create_params(fun, [hadoop_ip_dic['NN'][0]], cmd)
    ret = saltapi.main(params)
    ip_no = []
    for i, n in ret[0].iteritems():
        if not n:
            ip_no.append(i)
        print n
    if ip_no:
        sys.exit("refreshNodes失败\n%s" % [hadoop_ip_dic['NN'][0]])

    content = "refreshNodes完成\n"
    write_file(LOG_FILE, content)

def install(fun, ip_list):
    params = create_params(fun, ip_list)
    result = saltapi.main(params)
    res_dic = {}
    fail_dic = {}
    fail_tag = 0
   # print result
    alldata = result[0]
    try:
        for x in alldata:
            for n in  alldata[x]:
                #print alldata[x][n]['result']
                res_dic[x] = alldata[x][n]['result']
    except Exception,e:
    #    res_dic = alldata
        for m in alldata:
            print m
            print alldata[m]['result']
            res_dic[m] = alldata[m]['result']
    finally:
        for key,value in res_dic.items():
            #print key,value
            if not value:
                fail_tag += 1
                fail_dic[key] = value
        if fail_dic:
            sys.exit("%s失败个数%d，失败IP为%s"  % (fun,fail_tag,fail_dic))
        elif not res_dic:
            sys.exit("%s失败个数%d，失败IP为%s"  % (fun,fail_tag,fail_dic))
        else:
            print "%s成功" % fun

if __name__ == '__main__':
    os.system('cd %s && git pull &> /dev/null' % GIT_DIR)
    NAME_LIST = os.listdir(GIT_DIR)
    if HADOOP_NAME not in NAME_LIST:
        sys.exit("Git中不存在%s集群配置" % HADOOP_NAME)
    elif HBASE_NAME not in NAME_LIST:
        sys.exit("Git中不存在%s集群配置" % HBASE_NAME)

    # 获取集群IP地址，包括hadoop集群ip，hbase集群角色ip，hbase机架信息，hbase HM节点IP
    (hadoop_ip_dic, hbase_ip_dic, hbase_rack_dic) = get_ip()
    # print hadoop_ip_dic, hbase_ip_dic, hbase_rack_dic

    # 测试salt连通性，不通的直接停止操作
    salt_test(hbase_ip_dic['ALL'])

    # 同步minion端salt模块
    salt_update(hbase_ip_dic['ALL'])

    # 通过bashrc文件获取集群安装版本信息
    version_dic = hbase.get_version()

    # 同步bashrc文件
    sync_bashrc(hbase_ip_dic['ALL'])

    # 添加dns并获取dns字典
    dns_dic = set_dns(hbase_ip_dic['ALL'])

    # 通过salt模块安装hbase及hadoop
    install('HbaseExpansion.hbase_hadoop', hbase_ip_dic['ALL'])
    # install('HbaseExpansion.hbase', hbase_ip_dic['ALL'])

    # 修改本地git上面的hadoop、hbase配置文件
    set_hadoop_conf(dns_dic, hbase_rack_dic, version_dic)
    # set_hbase_conf(dns_dic, hbase_rack_dic, version_dic, hbase_ip_dic)

    # 将本地git修改push到远程
    git_push()

    # 同步ssh-key信息
    sync_ssh(hbase_ip_dic)

    # 同步配置文件
    # sync_hbase_conf(hbase_ip_dic)

    sync_hadoop_conf(hadoop_ip_dic)

    # 刷新node节点
    refresh_nodes(hadoop_ip_dic)


