#!/usr/bin/env python
#coding: utf-8
############################
#AUTHOR:zhangqiuying
#CREATED:2016-04-11
#UPDATE:2016-04-21

import time
import datetime
import os
import commands
import sys
import urllib,urllib2
import json
import re
from phenix_http import send

#ip_list=['172.22.99.101','172.22.99.102','172.19.153.49']
ret_num={"total":0,"success":0,"failed":0}
def get_ip(url):
    ip_list = []
    req = urllib2.Request(url)
    res = urllib2.urlopen(req).read()
    all_data = json.loads(res)
    detail_data = all_data['data']['dataList']
    for i in detail_data:
        ip_l = str(''.join(i['ip']))
        ip_list.append(ip_l)
    return ip_list
def checkifspeed():
    ip_list_all = []
    ip_list_nohd = []
    url_all = 'http://bdp.jd.com/ops/api/server/findAllServerList.ajax?appKey=123456&erp=zhangqiuying'
    #获得服务器管理所有IP列表
    ip_list_all = get_ip(url_all)

    tags_nohd = ['462','376','16','123','451','453','460','491','88','87','140','433','518','3','431']
    #获取服务器管理非hadoop运维IP列表
    for t in tags_nohd:
        url_nohd = 'http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=%s&appKey=123456&erp=zhangqiuying' % t
        ip_list_nohd.extend(get_ip(url_nohd))

    ip_list = list(set(ip_list_all).difference(set(ip_list_nohd)))
    ifstatus="IfOperStatus"
    ifspeed="ifhighspeed"
    #获取当前时间记录日志
    now = datetime.datetime.now()
    otherStyleTime = now.strftime("%Y-%m-%d %H:%M:%S")
    otherStyleTime_d = now.strftime("%Y-%m-%d")
    #日志文件
    f = "/root/ifspeed/ifspeed_check.log.%s" % otherStyleTime_d
    for ip in ip_list:
        ret_num['total'] = ret_num['total'] +1
        ret = {"result":0,"ip":"","details":""}
        ret['ip'] = ip
        (snmp_status,snmp_output) = commands.getstatusoutput("snmpwalk -v 2c -c 360buy %s %s" % (ip,ifstatus))
        if snmp_status:
            (ping_status,ping_output) = commands.getstatusoutput("ping -w5 -c3  %s" % ip)
            if ping_status:
                ret_num['success'] = ret_num['success'] + 1
                ret['result'] = 1
                ret['details'] = ret['details'] + 'poweroff'
                #send phenix
                metrick = 'ifspeed'
                metricv = 0
                dt = 'i'
                send(ip, metrick, metricv, dt)
            else:
                print i,"poweron"
                ret_num['failed'] = ret_num['failed'] + 1 
                ret['result'] = 1
                ret['details'] = ret['details'] + 'SNMP could not connect : %s ' % snmp_output
                #send phenix
                metrick = 'ifspeed'
                metricv = ret['details']
                dt = 's'
                send(ip, metrick, metricv, dt)
        else:
            (ifstatus_status,ifstatus_output) = commands.getstatusoutput("snmpwalk -v 2c -c 360buy %s %s| grep 'up'|grep -v '.1 ='|awk -F ':' '{print $3}'|sed 's/ifOperStatus//g'|sed 's/INTEGER//g'" % (ip,ifstatus))
            num = ifstatus_output.split('\n') 
            for n in num:
                (status,output) = commands.getstatusoutput("snmpwalk -v 2c -c 360buy %s %s|grep '%s'" % (ip,ifspeed,n))
                ret['details'] = ret['details'] + '%s; ' % output
                (ifspeed_status,ifspeed_output) = commands.getstatusoutput("snmpwalk -v 2c -c 360buy %s %s|grep '%s'|awk '{print $NF}'" % (ip,ifspeed,n))
                ifs = ifspeed_output.split('\n')
                tag = 0
                for s in ifs:
                    if s == '1000' or s == '10000':
                        tag = tag + 0
                    else:
                        tag = tag + 1
            if tag:
                ret_num['failed'] = ret_num['failed'] + 1
                ret['result']=1
                #send phenix
                metrick = 'ifspeed'
                metricv = ret['details']
                dt = 's'
                send(ip, metrick, metricv, dt)
            else:
                ret_num['success'] = ret_num['success'] + 1
                metrick = 'ifspeed'
                metricv = 0
                dt = 'i'
                send(ip, metrick, metricv, dt)
        #print ret
        #记录日志 单台IP
        ifspeed_status = "Time:%s Ifspeed_ret:%s" % (otherStyleTime, str(ret))
        wfile = open(f, 'a')
        wfile.write(str(ifspeed_status) + '\n')
        wfile.close()
    #return ret_num
    #记录日志 total
    ifspeed_total_status = "Time:%s Ifspeed_ret:%s" % (otherStyleTime, str(ret_num))
    wfile = open(f, 'a')
    wfile.write(str(ifspeed_total_status) + '\n')
    wfile.close()

checkifspeed()
