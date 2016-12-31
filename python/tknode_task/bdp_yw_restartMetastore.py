#!/usr/bin/python
#coding: utf-8

import sys
import json
import httplib,urllib;
import urllib2

salt_api_uri="http://172.22.88.20:8181"

ip=sys.argv[1]
user=sys.argv[-1]
start="su - " + user  + " -c \" nohup hive --service metastore &>> /data0/Logs/" + user + "/" + user + ".hive-meta-store.log &\""
def stop_metastore():
    try:
        dict1 = {"client":"local","tgt":ip,"fun":"cmd.run","arg":"su - " + user + " -c jps|grep RunJar|awk '{print $1}'|xargs kill -9"}
        d = urllib.urlencode(dict1)
        h = {"X-Auth-Token" : get_token(), "Accept":"application/x-yaml"}
        req = urllib2.Request("http://172.22.88.20:8181", d, headers=h)
        content = urllib2.urlopen(req).read()
        print content
        print "执行成功"
    except Exception,e:
        print "salt model error"
        print e
def start_metastore():
    try:
        #dict1 = {"client":"local","tgt":ip,"fun":"cmd.run","arg":"su - " + user + " -c jps|grep RunJar|awk '{print $1}'|xargs kill -9;nohup hive --service metastore > /data0/Logs/$USER/$USER.hive-meta-store.log &"}
        dict1={"client":"local","tgt":ip,"fun":"cmd.run","arg":start}
        d = urllib.urlencode(dict1)
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
        #print "get salt api error"
        print e

if __name__ == '__main__':
    stop_metastore()
    start_metastore()
