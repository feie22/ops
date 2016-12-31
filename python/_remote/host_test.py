#!/usr/bin/python
# coding:utf-8

"""
@description: stress test
@author: wangdelong@jd.com
@createtime: 16-11-24 下午3:06
@updatetime: 16-11-24 下午3:06
"""

import saltapi
import time

cur_time = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(time.time()))
ip_file = './ip.list'
result_file = './result_%s.log' % cur_time


def get_ip(ip_file):
    with open(ip_file) as f:
        ip_list = f.read().strip('\n').split('\n')
    ips = ','.join(ip_list)
    return ips, ip_list


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
    ips, ip_list = get_ip(ip_file)
    sync_module(ips)
    # print sync_module(ips)
    '''
    fun_list = ['stress_util.cpu',
                # 'stress_util.mem',
                'stress_util.diskread',
                'stress_util.diskwrite']

    for i in fun_list:
        params = create_params(i, ips)
        result = saltapi.main(params)
        print result
    '''
    with open(result_file, 'a') as f:
        par_cpu = create_params('stress_util.cpu', ips)
        ret_cpu = saltapi.main(par_cpu)
        for ip, ret in ret_cpu.iteritems():
            f.write(ip + '\t' + 'check item: cpu' + '\t' + str(ret['details']) + '\n')
        
        par_mem = create_params('stress_util.mem', ips)
        ret_cpu = saltapi.main(par_mem)
        for ip, ret in ret_cpu.iteritems():
            f.write(ip + '\t' + 'check item: mem' + '\t' + str(ret['details']) + '\n')
            
        par_diskread = create_params('stress_util.diskread', ips)
        ret_diskread = saltapi.main(par_diskread)
        for ip, ret in ret_diskread.iteritems():
            f.write(ip + '\t' + 'check item: diskread' + '\t')
            for i in ret['details']:
                f.write(i + '\t')
            f.write('\n')

        par_diskwrite = create_params('stress_util.diskwrite', ips)
        ret_diskwrite = saltapi.main(par_diskwrite)
        for ip, ret in ret_diskwrite.iteritems():
            f.write(ip + '\t' + 'check item: diskwrite' + '\t')
            for i in ret['details']:
                f.write(i + '\t')
            f.write('\n')

        par_network = create_params('stress_util.network', ips, ips)
        ret_net = saltapi.main(par_network)
        for ip, ret in ret_net.iteritems():
            f.write(ip + '\t' + 'check item: network' + '\t' + str(ret['details']) + '\n')



if __name__ == '__main__':
    stress()

