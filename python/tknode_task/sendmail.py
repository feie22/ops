#!/usr/bin/python
# -*- coding: utf-8 -*- 

import urllib2,urllib,sys
def POST_MAIL(*keys):
    params = {
        'appCode':'monitor',
        'erp':'pengxingbo',
        'address':'pengxingbo@jd.com,hbase@jd.com',
        'content':keys[1].replace('\n', '\r\n'),
        'subject':keys[0]
    }
    #print(params)
    req=urllib2.Request('http://bdp.jd.com/api/urm/mail/send.ajax',urllib.urlencode(params))
    ret=urllib2.urlopen(req)
    retread=ret.read()
    print retread

#filename = sys.argv[1]
#msg = open(filename).read()
#POST_MAIL('wireless_data_lost_file_list', msg)
title = sys.argv[1]
msg = sys.argv[2]
POST_MAIL('[buffalo] [' + title + ']' , msg)
