#!/usr/bin/python
#coding:utf-8

"""
@description: disk trouble report
@author: wangdelong@jd.com
@createtime: 16-11-7 3:14
@updatetime: ?
"""

import datetime
import json
import urllib
import salt.client


CLIENT = salt.client.LocalClient()
NOW = datetime.datetime.now()
TIME_STRING = NOW.strftime("%Y-%m-%d %H:%M:%S")
LOG_DIR = '/job/log/'
API_URL = 'http://t.zeus.jd.com/task/api/v1?data='


def salt_exec(ip_list, fun):
    """salt execute"""
    ret_dic = CLIENT.cmd(ip_list, fun, expr_form='list')
    return ret_dic


def ip_file(file):
    """read ip file as list"""
    with open(file) as f:
        ip_list = f.read().strip('\n').split('\n')
    return ip_list


def api_report(data_json):
    """call api execute report"""
    try:
        # get_par = urllib.quote(data_json)
        u = urllib.urlopen(API_URL + data_json)
        print u.read()
    except Exception, e:
        print e


def dic_list(dic, cat_id):
    """组织数据结构"""
    data_list = []
    for i, n in dic.iteritems():
        for k in n['details']:
            dic_item = {'ip': i, 'result': True, 'category_id': cat_id, 'status_id': '2',
                        'rec_time': TIME_STRING, 'opt_time': '',
                        'username': 'wangdelong5', 'channel': 'salt', 'details': k}
            data_list.append(dic_item)
    return data_list


def exec_report(fun, log_file, cat_id):
    ip_list = ip_file(log_file)
    if not ip_list[0]:
        return
    salt_exec(ip_list, 'saltutil.sync_modules')
    ret_dic = salt_exec(ip_list, fun)
    data_list = dic_list(ret_dic, cat_id)
    data_json = json.dumps(data_list)
    api_report(data_json)


def disk_readonly_report():
    fun = "check_util.reado"
    log_file = LOG_DIR + "bad_disk.log"
    cat_id = '1'
    exec_report(fun, log_file, cat_id)


def disk_miss_report():
    fun = "check_util.miss"
    log_file = LOG_DIR + "miss_disk.log"
    cat_id = '2'
    exec_report(fun, log_file, cat_id)


def net_err_report():
    fun = "check_util.net_err"
    log_file = LOG_DIR + "net_errors.log"
    cat_id = '6'
    exec_report(fun, log_file, cat_id)


def zombie_report():
    fun = "check_util.zombie"
    log_file = LOG_DIR + "zombie.log"
    cat_id = '7'
    exec_report(fun, log_file, cat_id)


if __name__ == '__main__':
    disk_readonly_report()
    disk_miss_report()
    # net_err_report()
    zombie_report()

