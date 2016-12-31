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

def exe_refresh_conf():
    try:
        d = urllib.urlencode({"client":"local","tgt":"172.22.84.104","fun":"refresh_conf.bayesFairscheduler"})
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
   exe_refresh_conf() 
