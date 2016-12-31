#!/usr/bin/env python
# encoding: utf-8

"""
@description: ?
@author: wangdelong@jd.com
@createtime: 2016/8/30 0030
@updatetime: ?
"""

import subprocess
import MySQLdb
import sys
import os

def exec_shell():
    cmd = "sh geterrorphysical.sh > error.log"
    ret = subprocess.call(cmd, shell=True)
    if ret:
        sys.exit("执行获取磁盘信息脚本失败")
    value = []
    f = open("physicaldisk_result.log")
    f_list = f.read().splitlines()
    for i in f_list:
        line_l = i.split()
        lien_t = tuple(line_l)
        value.append(lien_t)
    return value

def insert_mysql(value):
    try:
        conn = MySQLdb.Connect(host='172.22.178.98', user='root', passwd='hadoop', db='ja_hbase', charset='utf8')
        cur = conn.cursor()
        sql_i = "insert into disk_check (ip, host_sn, slot, type, vendor, modelname, disk_sn, status, blocks) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cur.executemany(sql_i, value)
        conn.commit()
        cur.close()
        conn.close()
    except MySQLdb.Error, e:
        print e
        # os.system('echo "Mysql Error %d: %s" >> %s ' % (e.args[0], e.args[1], "error.log"))


if __name__ == '__main__':
    value = exec_shell()
    # insert_mysql(value)