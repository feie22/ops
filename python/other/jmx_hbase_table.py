#! /usr/bin/env python
#coding=utf-8
import os
import simplejson as json
import httplib,urllib;
import time
import urllib2

res_host_master='172.22.166.102'
res_host_bakmaster='172.22.166.101'
res_host=''
tadbhost='172.22.182.21:4242'
hmJmxPre='hm_'
hostFile='hosts'
splitStr='-'
metricFile='metric'

def getJmx(host,cluster_name):
    try:
        jsonarr = []
        data=os.popen("curl -s http://"+ host +":60010/jmx?qry=hadoop:service=Master,name=Master  > ./"+ hmJmxPre + host +".txt").readlines()
        f = file(hmJmxPre + host + '.txt')
        source=f.read().strip()
        ddata=json.JSONDecoder().decode(source)
        target=ddata['beans']
        rs = target[0]['RegionServers']
        tableNames = []
        regionInfo = {}
        for i in rs:
            value = i['value']
            regionsLoad = value['regionsLoad']
            for j in regionsLoad:
                nameValues=j['value']
                nameAsString = nameValues['nameAsString']
                tableName = nameAsString.split(',')[0]
                #nameValues['tablename'] = tableName 
                regionInfo[nameAsString] = nameValues
                tableNames.append(tableName)
        tableNames = {}.fromkeys(tableNames).keys()
        tableInfos = {}
        for i in tableNames:
            for region in regionInfo:
                tableName = region.split(',')[0]
                if tableName == i :
                #print regionInfo[region]
                #print region
                    if tableInfos.has_key(tableName):
                        for info in  regionInfo[region]:
                            if (info != 'name') and (info != 'nameAsString'):
                                sun = tableInfos[tableName][info] + regionInfo[region][info]
                                tableInfos[tableName][info] = sun
                    else:
                        tableInfos[tableName] = regionInfo[region]
    
         
        for i in tableInfos:
            for j in tableInfos[i]:
                if (j != 'name') and (j != 'nameAsString'):
                    metricK = cluster_name +'.table.' + j 
                    metricV = tableInfos[i][j]
                    tag = {"table": i}
                    jmx = metric(metricK,metricV ,tag)
                    jsonarr.append(jmx)
            
            jsonstr= getJosn(jsonarr)
            put(jsonstr)
            jsonarr = []

    except Exception,e:
        print e


    
def put(jmx):
    params = jmx;#'[{\"metric\": \"sys.cpu.nice\", \"timestamp\":  1405322499000,\"value\": 16, \"tags\": {  \"host\": \"web01\",  \"dc\": \"lga\" } }]';
    headerdata = {"Content-Type":"application/x-www-form-urlencoded", "Connection":"Keep-Alive"};  
    #print len(params)
    conn = httplib.HTTPConnection(tadbhost);    

    conn.request("POST","/api/put?details",params,headerdata);   
    response = conn.getresponse();
    #print response.status  
    #print response.reason  
    #print response.read()  
    conn.close();   

def metric(metric,value,tag):
    timestamp = int(time.time()*1000)
    #message.append("tags" ,tag)
    return  json.dumps({"metric": metric , "timestamp":  timestamp ,"value": value , "tags": tag })

def addmetric(cluster_name):
    f = open(metricFile)
    for i in f:
        url = 'http://'+tadbhost+'/api/uid/assign?metric='+cluster_name + ".table." + i
        res = os.popen("curl -s " + url)
        print res

def doJob():
    flag = 0
    while True :
#        time.sleep(30)
        try:
            metricf = file(hostFile)
            jsonarr = []
            for i in metricf.readlines():   
                metricArr = i.strip('\n').split(splitStr)
                master = metricArr[0]
                back_master = metricArr[2]
                cluster_name = metricArr[1]
                host_master = getMaster(master,back_master)
                print host_master                
                if flag:
                    addmetric(cluster_name)
                start = time.time()
                print start
                getJmx(host_master,cluster_name) 
                end = time.time()
                print end - start
        except   BaseException,e:
            print "error:",e
        flag = 0 

def getJosn(jsonarr):
    jsonStr = '['
    for i in jsonarr:
        jsonStr += i + ','
    return jsonStr[:-1] + ']'

def getRes(hm_host):
    data=os.popen("curl -s http://"+ hm_host +":60010/jmx?qry=hadoop:service=Master,name=Master  > ./"+ hmJmxPre + hm_host +".txt").readlines()
    f = file(hmJmxPre+hm_host+'.txt')
    source=f.read().strip()
    ddata=json.JSONDecoder().decode(source)
    target=ddata['beans']
    rs = target[0]['RegionServers']
    return rs

        
def getMaster(master,back_master):
    data=os.popen("curl -s http://"+ master +":60010/jmx?qry=hadoop:service=Master,name=Master").readlines()
    if len(data) == 3 :
        return back_master
    else:
        return master
    
if __name__== '__main__':
    print "begin.."
    # doJob()
    #getTableName()
    #addmetric()
    getJmx('172.22.169.61','sleep')
