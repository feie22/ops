#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: zhangqiuying
@data:2016-04-15
#update:
'''

import time
import datetime
import httplib
import json
import urllib


def send(cluster_name, metricK, metricV, dt):
    url = "bdp.jd.com"
    timestamp = int(time.time()*1000)
    params = {'monitorData' : json.dumps({'mr': 'hbase_check','tp': '004','t': timestamp ,'lc': {'s_1_k': '集群巡检结果' ,'s_1_n': '集群巡检结果'}, 'me':  [{'lc': {'s_1_k': cluster_name ,'s_1_n': cluster_name}, 'me':  [{'k': metricK,'v': metricV,'n': metricK,'dt': dt}]}]})}
    headerdata = {"Content-Type":"application/x-www-form-urlencoded", "Connection":"Keep-Alive"}
    server = httplib.HTTPConnection(url)
    server.request("POST","/phenix/collector/monitorData.ajax",urllib.urlencode(params),headerdata)
    response = server.getresponse()
    print response.status
    print response.reason
    print response.read()
    #获取当前日志记录日志
    now = datetime.datetime.now()
    otherStyleTime = now.strftime("%Y-%m-%d %H:%M:%S")
    otherStyleTime_d = now.strftime("%Y-%m-%d")
    #日志文件
    f = "/job/tmp/test_status_phenix_api.log.%s" % otherStyleTime_d
    response_status = "Time:%s IP:%s r_s:%s" % (otherStyleTime,cluster_name,response.status)
    #记录日志 接口调用状态
    wfile = open(f, 'a')
    wfile.write(str(response_status) + '\n')
    wfile.close()
    server.close()

send('wdl', '磁盘使用率', 100, 'i')