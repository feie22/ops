#!/usr/bin/python
#coding: utf-8

import sys
import json
import httplib,urllib;
import urllib2

salt_api_uri="http://172.22.88.20:8181"

ip=sys.argv[1]
user=sys.argv[-1]
log="/data0/Logs/" + user + "/" + user + ".hive-meta-store.log"

print log
