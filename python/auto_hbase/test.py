#!/usr/bin/env python
# encoding: utf-8

"""
@description: test
@author: wangdelong@jd.com
@createtime: 2016/8/24 0024
@updatetime: ?
"""

import urllib
import json
import re
import sys
import os
import saltapi
import commands
import time

ip_file = "ip.list"

def create_params(fun,ip_list,*args):
    num = 1
    params = {
        'tgt': ','.join(ip_list),
        'fun': fun
        }
    if len(args) != 0:
        for arg in args:
            params['arg'+str(num)] = arg
            num += 1
    return params

def get_ip():
    f = open(ip_file)
    ip_list = f.read().splitlines()
    return  ip_list

def test():
    # fun1 = "cp.get_dir"
    # arg1 = "salt://auto-test/software" %
    # arg2 = "/"
    '''
    fun1 = "cmd.run"
    arg1 = "pwd"
    params = create_params(fun1, get_ip(), arg1)
    ret = saltapi.main_async(params)
    jid = ret[0]['jid']
    print jid
    ret_job = saltapi.main_job(jid)
    print ret_job
    '''
    ip_list = ['172.19.103.115', '172.19.103.114']
    ret = saltapi.main_key(ip_list)
    print ret

if __name__ == '__main__':
    test()