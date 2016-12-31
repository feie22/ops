#!/usr/bin/env python
#coding: utf-8
############################
#AUTHOR:zhangqiuying
#CREATED:2016-04-22
#UPDATE:
import os
import commands
import sys
import urllib,urllib2
import json
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
def open_monitor():
    tag_stop_monitor = '518'
    url_stop_monitor = 'http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=%s&appKey=123456&erp=zhangqiuying' % tag_stop_monitor
    ip_list_stop_monitor = get_ip(url_stop_monitor)
    for ip in ip_list_stop_monitor:
        ret = {"result":"","ip":"","details":""}
        ret['ip'] = ip
        (ping_status,ping_output) = commands.getstatusoutput("ping -w5 -c3  %s" % ip)
        if ping_status:
            ret['result'] = "POWEROFF"
            ret['details'] = "POWEROFF,Don't DeleteTags Zeus"
        else:
            ret['result'] = "POWERON"
            (status,output) = commands.getstatusoutput('curl -s "http://bdp.jd.com/ops/api/server/batchDeleteTagsByIPs.ajax?ips=%s&tags=%s&appKey=123456&erp=zhangqiuying"' % (ip,tag_stop_monitor))
            if status:
                ret['details'] = "POWERON,DeleteTags Zeus failed!"
            else:
                ret['details'] = "POWERON,DeleteTags Zeus successful!"
        print ret
open_monitor()
