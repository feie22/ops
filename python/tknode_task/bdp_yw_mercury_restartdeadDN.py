#!/usr/bin/python
# coding=utf-8
# author by fanshiyi
# 2016-04-08
import sys
import urllib
import urllib2
import json
import socket
nn=sys.argv[-1]
#print nn
url='http://%s:50070/jmx?qry=Hadoop:service=NameNode,name=NameNodeInfo' % nn
salt_api_uri="http://172.19.185.84:8181"
def getnodes():
    rep=urllib2.urlopen(url).read()
    data=json.loads(rep)
    list=eval((data["beans"][0]["DeadNodes"]).replace('false','"false"')).keys()
    ip_list=[]
    for host in list:
        #print host
        ip=socket.gethostbyname(host)
        ip_list.append(ip)
    #print ip_list
    #tgt=','.join(ip_list)
    #print tgt
    return ip_list
getnodes()
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
def restartDeadDN():
    ip_list=getnodes()
    for ip in ip_list:
        try:
            dict1={"client":"local","tgt":ip,"fun":"cmd.run","arg":"su - hadp -c \"hadoop-daemon.sh stop datanode;sleep 1;hadoop-daemon.sh start datanode\" "}
            #dict1={"client":"local","tgt":ip,"fun":"cmd.run","arg":"su - hadp -c \"cat /etc/issue;ls\""}
            #dict1["tgt"]=getnodes()
            #print dict1
            #print type(dict1)
            d = urllib.urlencode(dict1)
            h = {"X-Auth-Token" : get_token(), "Accept":"application/x-yaml"}
            req = urllib2.Request("http://172.19.185.84:8181", d, headers=h)
            content = urllib2.urlopen(req).read()
            print content
            print "执行成功"
        except Exception,e:
            print "salt model error"
            print e
restartDeadDN()
