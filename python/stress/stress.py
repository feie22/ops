#!/usr/bin/python
# coding:utf-8

"""
@description: stress test
@author: wangdelong@jd.com
@createtime: 16-11-24 下午3:06
@updatetime: 16-11-24 下午3:06
"""

import saltapi


ip_file = './ip.list'

def get_ip(ip_file):
    with open(ip_file) as f:
        ips = f.read().replace('\n', ',')
    return ips


def create_params(fun, ips, *args):
    num = 1
    params = {'tgt': ips, 'fun': fun}
    if len(args) != 0:
        for arg in args:
            params['arg'+str(num)] = arg
            num += 1
    # print params
    return params


def sync_module(ips):
    params = create_params('saltutil.sync_modules', ips)
    return saltapi.main(params)


def stress():
    ips = get_ip(ip_file)
    print sync_module(ips)
    fun_list = [{'func': 'stress_util.cpu', 'args': []},
                # {'func': 'stress_util.mem', 'args': []},
                {'func': 'stress_util.diskread', 'args': []},
                {'func': 'stress_util.diskwrite', 'args': []},
                {'func': 'stress_util.network', 'args': [ips, ]}]

    for i in fun_list:
        for func, args in i:
            params = create_params(func, ips, args)
            result = saltapi.main(params)
            print result


if __name__ == '__main__':
    stress()

