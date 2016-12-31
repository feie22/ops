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
import socket
import json
import urllib

url="bdp.jd.com"
def send(ip, metricK, metricV, dt):
    timestamp = int(time.time()*1000)
    params = {'monitorData' : json.dumps({'mr': 'ifspeed_monitor','tp': '004','t': timestamp ,'lc': {'s_1_k': '网卡速率状态' ,'s_1_n': '网卡速率状态'}, 'me':  [{'lc': {'s_1_k': ip ,'s_1_n': ip}, 'me':  [{'k': metricK,'v': metricV,'n': metricK,'dt': dt}]}]})}
    headerdata = {"Content-Type":"application/x-www-form-urlencoded", "Connection":"Keep-Alive"}
    server = httplib.HTTPConnection(url)
    server.request("POST","/phenix/collector/monitorData.ajax",urllib.urlencode(params),headerdata)
    response = server.getresponse()
    #获取当前日志记录日志
    now = datetime.datetime.now()
    otherStyleTime = now.strftime("%Y-%m-%d %H:%M:%S")
    otherStyleTime_d = now.strftime("%Y-%m-%d")
    #日志文件
    f = "/root/ifspeed/ifspeed_status_phenix_api.log.%s" % otherStyleTime_d
    response_status = "Time:%s IP:%s r_s:%s" % (otherStyleTime,ip,response.status)
    #记录日志 接口调用状态
    wfile = open(f, 'a')
    wfile.write(str(response_status) + '\n')
    wfile.close()
    server.close()
