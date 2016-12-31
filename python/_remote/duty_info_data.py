#!/usr/bin/env python
# encoding: utf-8

"""
@description: 数据运维服务部排班表
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
h = 0
k = 0
v = []
l1 = ['董子铭', '张航', '高田田', '李小刚', '梁志超', '马千里']
l2 = [['张航', '15311471285'], ['高田田', '18500788507'],
      ['李小刚', '13269113385'], ['梁志超', '13021931989'],
      ['马千里', '18612801567'], ['董子铭', '18610382747']]
w_dic = {0:'星期日', 1:'星期一', 2:'星期二', 3:'星期三', 4:'星期四', 5:'星期五', 6:'星期六'}
while i <= (date2-date1+m):
    d = (date1+i-m).strftime('%Y-%m-%d')
    w = int((date1+i-m).strftime('%w'))
    ws = int((date1 + i - m).strftime('%W')) + 1
    h = h % 7
    if h == 0:
        k += 1
        l2.append(l2[0])
        l2.pop(0)
    k = k % 6
    v.append((l1[k], l2[h % 6][0], d, l2[h % 6][1], w_dic[w], ws))
    # print l1[k], l2[h % 6][0], d, l2[h % 6][1], w_dic[w]
    i += m
    h += 1

try:
    conn = MySQLdb.Connect(host='172.22.178.98', user='root', passwd='hadoop', db='ja_hbase', charset='utf8')
    cur = conn.cursor()
    cur.executemany('insert into Duty_Data (DAY_NAME, Night_NAME, DATE, PHONE, WEEK, WEEKS) values(%s,%s,%s,%s,%s,%s)', v)
    conn.commit()
    cur.close()
    conn.close()
except MySQLdb.Error, e:
    os.system('echo "Mysql Error e.args[0]: e.args[1]"')

