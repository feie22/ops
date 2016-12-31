#!/usr/bin/python
#coding:utf-8
#===============================================================================
#         FILE: run.py
#  DESCRIPTION: 执行脚本
#       AUTHOR: anbaoyong
#      VERSION: 1.0
#      CREATED: 2015-12-02
#       METHOD:  python run.py clustername clusterId
#===============================================================================

import urllib,urllib2
import json
import re
import sys
import socket
import saltapi
#流程中心获取数据
#url = "http://atom.bdp.jd.local/api/form/getdatas?appId=autoops&time=1440048055022&token=YEPWO7PQWO53K&data={requestId:"+str(16808)+"}"
#req = urllib2.Request(url)
#res = urllib2.urlopen(req).read()
#all_data = json.loads(res)
#need_data = all_data['list'][0]['bizData']['businessDetail1']['subData']
#print need_data[6]['col_7'][5:]
#

##服务器管理获取数据
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
            # sys.exit(1)
        ip_rack_dic[ip_rack['ip']] = "/rack/rack" + rack_num
    return ip_rack_dic
    


def create_params(fun,url,*args):
    '''
        生成saltapi接口参数
    '''
    num = 1
    ip_list = get_ip_rack(url).keys()
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

#saltapi.main(create_params('test.ping',append_url))
#saltapi.main(create_params('state.sls',append_url,'for'))
def run(step):
    '''
        执行步骤列表，执行失败退出，打印失败个数与ip
        res_dic：执行结果
        fail_dic：失败结果
        res_dic不为空fail_dic为空，表示无失败
        res_dic为空表示返回值格式不对
    '''
    for num in sorted(step.keys()):
        #result = json.loads(saltapi.main(step[num]))
        result = saltapi.main(step[num])
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
                print u"第%s步失败个数%d，失败IP为%s"  % (num,fail_tag,fail_dic)
                break
            elif not res_dic:
                print u"第%s步失败个数%d，失败IP为%s"  % (num,fail_tag,fail_dic)
                break
            else:
                print u"第%s步成功" % num 
            

    
if __name__ == '__main__':
    clustername = sys.argv[1]
    clusterId = sys.argv[2]
    print clustername ,clusterId
    zk_url = 'http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=%s,10&appKey=123456&erp=anbaoyong'  % clusterId
    cluster_url = 'http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=%s&appKey=123456&erp=anbaoyong'  % clusterId
    hbase_step = {
     1:create_params('cmd.run',cluster_url,'yum -y install net-snmp-python'),
     2:create_params('HbaseInstall.hbase_zk',zk_url),
     3:create_params('HbaseInstall.hbase_hadoop',cluster_url),
     4:create_params('HbaseInstall.hbase',cluster_url),
     5:create_params('HbaseConf.zk_conf',zk_url,clusterId),
     6:create_params('HbaseConf.hadoop_conf',cluster_url,clustername,clusterId)
    }
    run(hbase_step)
