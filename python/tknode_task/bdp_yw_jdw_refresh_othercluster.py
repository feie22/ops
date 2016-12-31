#!/usr/bin/python
#coding: utf-8

import os
import commands
import json
import hashlib
import simplejson as json
import httplib,urllib;
import time
import urllib2
import time

salt_api_uri="http://172.22.88.20:8181"
ip_list=['172.22.171.13','172.22.171.16','172.22.168.99','172.22.168.100','172.22.168.101','172.22.168.102','172.22.167.67','172.22.167.68','172.22.167.69','172.22.167.70']
def exe_refresh_conf():
    for ip in ip_list:
        try:
            d = urllib.urlencode({"client":"local","tgt":ip,"fun":"refresh_conf.jdwothercluster"})
            h = {"X-Auth-Token" : get_token(), "Accept":"application/x-yaml"}
            req = urllib2.Request("http://172.22.88.20:8181", d, headers=h)
            content = urllib2.urlopen(req).read()
            print content
            print "执行成功"
        except Exception,e:
            print "salt model error"
            print e
        print ip
#检测绿色通道的刷新是否影响到白名单
def check_whitelist():
    try:
        d = urllib.urlencode({"client":"local","tgt":"172.22.182.39","fun":"cmd.run","arg":"su - hadp -c 'hdfs dfs -ls hdfs://ns1;hdfs dfs -ls hdfs://ns2;hdfs dfs -ls hdfs://ns3;hdfs dfs -ls hdfs://ns4;hdfs dfs -ls hdfs://ns5'"})
        h = {"X-Auth-Token" : get_token(), "Accept":"application/x-yaml"}
        req = urllib2.Request("http://172.22.88.20:8181", d, headers=h)
        content = urllib2.urlopen(req).read()
        print content
        print "执行成功"
    except Exception,e:
        print "salt model error"
        print e

def get_token():
    try:
        d = urllib.urlencode({"username":"salt","password":"MXBe59Mpr0{G>!!$N.E{X4X#j","eauth":"pam"})
        req = urllib2.Request(salt_api_uri + "/login", d)
        content = urllib2.urlopen(req).read()
        ddata=json.JSONDecoder().decode(content)
        target=ddata['return'][0]['token']
        return target
    except Exception,e:
        print "get salt api error"
        print e

if __name__ == '__main__':
   exe_refresh_conf() 
   check_whitelist()
