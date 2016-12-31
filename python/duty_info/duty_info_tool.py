#!/usr/bin/env python
# encoding: utf-8

"""
@description: 运维工具研发部排班表
@author: wangdelong@jd.com
@createtime: 2016/7/7 0007
@updatetime: ?
"""
import datetime
import MySQLdb
import os

date1 = datetime.datetime.strptime('2017-01-02','%Y-%m-%d')
date2 = datetime.datetime.strptime('2017-12-31','%Y-%m-%d')
i = datetime.timedelta(days=1)
m = datetime.timedelta(1)
d = datetime.timedelta(7)
h = 0
v = []
m_list = [['滕爽', '17090140091', '13717957446'], ['朱林海', '17090140091', '15057117273']]
while i <= (date2-date1+m):
    s_date = (date1+i-m).strftime('%Y-%m-%d')
    e_date = (date1+i-m+d-m).strftime('%Y-%m-%d')
    w = int((date1+i-m).strftime('%W')) + 1
    h = h % 2
    v.append((m_list[h][0], s_date, e_date, w, m_list[h][1], m_list[h][2]))

    i += d
    h += 1

try:
    conn = MySQLdb.Connect(host='172.22.178.98', user='root', passwd='hadoop', db='ja_hbase', charset='utf8')
    cur = conn.cursor()
    cur.executemany('insert into Duty_Tool (NAME, S_DATE, E_DATE, WEEKS, PUB_PHONE, OWN_PHONE) values(%s,%s,%s,%s,%s,%s)', v)
    conn.commit()
    cur.close()
    conn.close()
except MySQLdb.Error, e:
    os.system('echo "Mysql Error e.args[0]: e.args[1]"')

