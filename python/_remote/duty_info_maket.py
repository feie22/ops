#!/usr/bin/env python
# encoding: utf-8

"""
@description: 集市运营组值班排期表
@author: wangdelong@jd.com
@createtime: 2016/9/27 0007
@updatetime: ?
"""
import datetime
import MySQLdb
import os

date1 = datetime.datetime.strptime('2016-12-19','%Y-%m-%d')
date2 = datetime.datetime.strptime('2017-12-31','%Y-%m-%d')
i = datetime.timedelta(days=1)
m = datetime.timedelta(1)
d = datetime.timedelta(7)
h = 0
v = []
m_list = [['白贤锋', '15910632077', '汪伟', '13043469509'], ['曹明爽', '13466527378', '刘译鸿', '18511254523'], ['杨泽森', '18518759221', '耿梦', '13718328152']]
while i <= (date2-date1+m):
    s_date = (date1+i-m).strftime('%Y-%m-%d')
    e_date = (date1+i-m+d-m).strftime('%Y-%m-%d')
    w = int((date1+i-m).strftime('%W')) + 1
    h = h % 3
    v.append((m_list[h][0], m_list[h][1], m_list[h][2], m_list[h][3], s_date, e_date, w))

    i += d
    h += 1

try:
    conn = MySQLdb.Connect(host='172.22.178.98', user='root', passwd='hadoop', db='ja_hbase', charset='utf8')
    cur = conn.cursor()
    cur.executemany('insert into Duty_Maket (NAME1, PHONE1, NAME2, PHONE2, S_DATE, E_DATE, WEEKS) values(%s,%s,%s,%s,%s,%s,%s)', v)
    conn.commit()
    cur.close()
    conn.close()
except MySQLdb.Error, e:
    os.system('echo "Mysql Error e.args[0]: e.args[1]"')

