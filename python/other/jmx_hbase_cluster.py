#! /usr/bin/env python
#coding=utf-8
'''
Created on 2014Äê9ÔÂ28ÈÕ

@author: wangensheng
'''
import os
import simplejson as json
import httplib,urllib;
import time
import urllib2
import time


tadbhost='172.22.182.21:4242'
hmJmxPre='hm_'
rpcPre='rpc_'
#hostFile='/root/wes/python/hbase_cluster/hosts'
hostFile='hosts'
#metricFile='/root/wes/python/hbase_cluster/metric'
metricFile='metric'
splitStr='-'

def getJmx(host,cluster_name,numberOfRequests):
    try:
        data=os.popen("curl -s http://"+ host +":60030/jmx?qry=hadoop:service=RegionServer,name=RegionServerStatistics  > ./"+ host +".txt").readlines()
        f = file(host+'.txt')
        source=f.read().strip()
        ddata=json.JSONDecoder().decode(source)
        target=ddata['beans']
        metricf = file(metricFile)
        jsonarr = []
        for i in metricf.readlines():
            tmp = i.strip('\n')
            metricK = cluster_name +'.' + tmp
            metricV = 0
            #print metricK
            #print '==============='
            if tmp.startswith("Rpc"):
                metricV = getRpc(host,cluster_name,tmp)
            elif tmp.startswith("numberOfRequests"):
                metricV = numberOfRequests
            else:
                metricV = target[0][tmp]

            jmx = metric(metricK,metricV ,host)
            jsonarr.append(jmx)
        jsonstr= getJosn(jsonarr)
        put(jsonstr)
    except Exception,e:
        print e

def getRpc(host,cluster_name,metricK):
    data=os.popen("curl -s http://"+ host +":60030/jmx?qry=hadoop:service=HBase,name=RPCStatistics-60020  > ./"+ host +".txt").readlines()
    f = file(host+'.txt')
    source=f.read().strip()
    ddata=json.JSONDecoder().decode(source)
    target=ddata['beans']
    metricf = file(metricFile)
    return target[0][metricK]
    
def put(jmx):
    params = jmx;#'[{\"metric\": \"sys.cpu.nice\", \"timestamp\":  1405322499000,\"value\": 16, \"tags\": {  \"host\": \"web01\",  \"dc\": \"lga\" } }]';
    headerdata = {"Content-Type":"application/x-www-form-urlencoded", "Connection":"Keep-Alive"};  
    conn = httplib.HTTPConnection(tadbhost);    

    conn.request("POST","/api/put?details",params,headerdata);   
    response = conn.getresponse();
 #   print response.status  
 #   print response.reason  
 #   print response.read()  
    conn.close();   

def metric(metric,value,host):
    timestamp = int(time.time()*1000)
    return  json.dumps({"metric": metric , "timestamp":  timestamp ,"value": value , "tags": { "host": host } })

def addmetric(cluster_name):
    f = open(metricFile)
    for i in f:
        url = 'http://'+tadbhost+'/api/uid/assign?metric='+cluster_name + "." + i
        res = os.popen("curl -s " + url)
#        print res

def doJob():
     
    flag = 1
    while True:
        metricf = file(hostFile)
        jsonarr = []
        try:
            for i in metricf.readlines():
                print i
                metricArr = i.strip('\n').split(splitStr)
                cluster_name = metricArr[0]
                res_host_master = metricArr[1]
                res_host_bakmaster = metricArr[2]
                master = getMaster(res_host_master,res_host_bakmaster)
                if flag:
                    addmetric(cluster_name)
                    print "addmetric ok"
                rs = getRes(master)
                for i in rs:
                    rsTmp = i['key']
                    rshost = rsTmp.split(',')[0]
                    rsTmpV = i['value']
                    numberOfRequests = rsTmpV['numberOfRequests']
                    getJmx(rshost,cluster_name,numberOfRequests)
        except Exception,ex:
            print ex
            raise
            print "error"
        flag = 0
        time.sleep(15)
    
'''    
    addmetric(cluster_name)
    rs = getRes(hm_host)

    while True :
        for i in rs:
            rsTmp = i['key']
            rshost = rsTmp.split(',')[0]

            rsTmpV = i['value']
            numberOfRequests = rsTmpV['numberOfRequests']
            getJmx(rshost,cluster_name,numberOfRequests)
        rs = getRes(hm_host)
        time.sleep(5)
'''
def getJosn(jsonarr):
    jsonStr = '['
    for i in jsonarr:
        jsonStr += i + ','
    return jsonStr[:-1] + ']'

def getRes(hm_host):
    print hm_host
    data=os.popen("curl -s http://"+ hm_host +":60010/jmx?qry=hadoop:service=Master,name=Master  > ./"+ hmJmxPre + hm_host +".txt").readlines()
    f = file(hmJmxPre+hm_host+'.txt')
    source=f.read().strip()
    ddata=json.JSONDecoder().decode(source)
    target=ddata['beans']
    rs = target[0]['RegionServers']
    return rs

def getMaster(res_host_master,res_host_bakmaster):
    data=os.popen("curl -s http://"+ res_host_master +":60010/jmx?qry=hadoop:service=Master,name=Master").readlines()
    if len(data) == 3 :
        return res_host_bakmaster
    else:
        return res_host_master


def getReqNo(rs):
    for i in rs :
        rsTmp = i['value']
        numberOfRequests = rsTmp['numberOfRequests']
        

if __name__== '__main__':
    #put()
    #getJmx()
    #print metric('aaa',12,'node31')
    #addmetric()
    doJob()
    #print getRpc('172.17.44.14','first','RpcQueueTimeAvgTime')

