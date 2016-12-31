#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: yangming3
'''

import time
import httplib
import time
import socket
import json
import urllib
from simpleLog import FinalLogger as metricLog

class PhenixHttp(object):
    def __init__(self, url="bdp.jd.com"):
        self.url = url
        self.logger = metricLog.getLogger()
        #self.server = httplib.HTTPConnection(url)
        #self.server.connect()

    def send(self, cluster_name, metricK, metricV, dt):
        timestamp = int(time.time()*1000)
        params = {
        #'monitorData' : json.dumps({'mr': 'hbase_monitor','tp': '004','t': timestamp ,'lc': {'s_1_k': cluster ,'s_1_n': cluster}, 'me':  [{'k': metrick,'v': metricv,'n': metrick,'dt': dt}]})
        'monitorData' : json.dumps({'mr': 'hbase_monitor','tp': '004','t': timestamp ,'lc': {'s_1_k': 'HBase集群状态' ,'s_1_n': 'HBase集群状态'}, 'me':  [{'lc': {'s_1_k': cluster_name ,'s_1_n': cluster_name}, 'me':  [{'k': metricK,'v': metricV,'n': metricK,'dt': dt}]}]})
        }
        #timestamp = int(time.time())
        headerdata = {"Content-Type":"application/x-www-form-urlencoded", "Connection":"Keep-Alive"};
       
        #testWrite(params)
        #self.logger.info(params)
         
        server = httplib.HTTPConnection(self.url)
        try:
            
            server.request("POST","/phenix/collector/monitorData.ajax",urllib.urlencode(params),headerdata);
            response = server.getresponse();
            
            #self.logger.info('status: ['+str(response.status)+'] reason: ['+response.reason+'] response: ['+response.read()+']')
            self.logger.info('cluster: ['+cluster_name+'] '+'metric: ['+str(metricK)+'] value: ['+str(metricV)+'] response: ['+response.read()+'] & time: ['+str(timestamp)+']')
            
            '''
            print response.status
            print response.reason
            print response.read()
            '''
        except socket.error as msg:
            #print 'ERROR:', msg
            self.logger.error(msg)
        server.close()

def testWrite(params):
    wfile = open('wf2.txt', 'a')
    wfile.write(str(params) + '\n')
    wfile.close()
