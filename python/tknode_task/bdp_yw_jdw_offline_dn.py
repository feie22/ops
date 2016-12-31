#!/usr/bin/python
#coding: utf-8

import sys
import json
import httplib,urllib;
import urllib2

salt_api_uri="http://172.22.99.100:8181"
cluster_name="jdw"
#ns_name=['ns1','ns2','ns3','ns4','ns5']
ns_name=['ns1']
rm_ip_all="172.22.99.101"
rm_ip_master="172.22.99.101"

def fileserver_update():
    try:
        #d = urllib.urlencode({"client":"runner","fun":"fileserver.file_list"})
        d = urllib.urlencode({"client":"runner","fun":"fileserver.update"})
        h = {"X-Auth-Token" : get_token(), "Accept":"application/x-yaml"}
        req = urllib2.Request(salt_api_uri, d, headers=h)
        content = urllib2.urlopen(req).read()
        print content
        print "执行成功"
    except Exception,e:
        print "salt model error"
        print e

def ns_files_sync():
    for ns in ns_name:
        try:
            #d = urllib.urlencode({"client":"local","tgt": cluster_name + "_" + ns + "_nn","expr_form":"nodegroup","fun":"state.sls","arg": cluster_name + ".sls." + ns})
            d = urllib.urlencode({"client":"local","tgt": cluster_name + "_" + ns + "_nn","expr_form":"nodegroup","fun":"state.sls","arg": cluster_name + ".sls." + ns})
            #d = urllib.urlencode({"client":"local","tgt":"jdw_ns1_nn","expr_form":"nodegroup","fun":"state.sls","arg": "jdw.sls.ns1"})
            #d = urllib.urlencode({"client":"local","tgt":"jdw_ns1_nn","expr_form":"nodegroup","fun":"cmd.run","arg": "ifconfig"})
            h = {"X-Auth-Token" : get_token(), "Accept":"application/x-yaml"}
            req = urllib2.Request(salt_api_uri, d, headers=h)
            content = urllib2.urlopen(req).read()
            print content
            print "执行成功"
        except Exception,e:
            print "salt model error"
            print e
def rm_files_sync():
    try:
        d = urllib.urlencode({"client":"local","tgt":rm_ip_all,"fun":"state.sls","arg": cluster_name + ".sls.rm" })
        h = {"X-Auth-Token" : get_token(), "Accept":"application/x-yaml"}
        req = urllib2.Request(salt_api_uri, d, headers=h)
        content = urllib2.urlopen(req).read()
        print content
        print "执行成功"
    except Exception,e:
        print "salt model error"
        print e
def cluster_refreshdfsnode():
    for ns in ns_name:
        try:
            d = urllib.urlencode({"client":"local","tgt": cluster_name + "_" + ns + "_nn","expr_form":"nodegroup","fun":"cluster.refreshdfsnode"})
            h = {"X-Auth-Token" : get_token(), "Accept":"application/x-yaml"}
            req = urllib2.Request(salt_api_uri, d, headers=h)
            content = urllib2.urlopen(req).read()
            print content
            print "执行成功"
        except Exception,e:
            print "salt model error"
            print e
def cluster_refresyarnnode():
    for ns in ns_name:
        try:
            d = urllib.urlencode({"client":"local","tgt":rm_ip_master,"fun":"cluster.refreshyarnnode"})
            h = {"X-Auth-Token" : get_token(), "Accept":"application/x-yaml"}
            req = urllib2.Request(salt_api_uri, d, headers=h)
            content = urllib2.urlopen(req).read()
            print content
            print "执行成功"
        except Exception,e:
            print "salt model error"
            print e
def get_token():
    try:
        d = urllib.urlencode({"username":"salt","password":"1qaz@WSX","eauth":"pam"})
        req = urllib2.Request(salt_api_uri + "/login", d)
        content = urllib2.urlopen(req).read()
        ddata=json.JSONDecoder().decode(content)
        target=ddata['return'][0]['token']
        return target
    except Exception,e:
        #print "get salt api error"
        print e

if __name__ == '__main__':
    fileserver_update()
    ns_files_sync()
    rm_files_sync()
    #cluster_refreshdfsnode()
    #cluster_refresyarnnode()
