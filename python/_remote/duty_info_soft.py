#!/usr/bin/env python
# encoding: utf-8

"""
@description: 运维工具研发部平台软件运维排班表
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
# l1 = ['董子铭', '张航', '高田田', '李小刚', '梁志超', '马千里']
l1 = [['唐尚文', '17080151318'], ['吴彪', '18810848987'], ['张芒', '13564187517'],
      ['白冰', '18211100183'], ['郑晨宇', '18600459673'], ['孟兆飞', '13501035843'],
      ['张瑜标', '17090889538'], ['吴怡燃', '13521941986'], ['李成飞', '18211172579'],
      ['王哲涵', '15331671063'],]
# w_dic = {0:'星期日', 1:'星期一', 2:'星期二', 3:'星期三', 4:'星期四', 5:'星期五', 6:'星期六'}
while i <= (date2-date1+m):
    d = (date1+i-m).strftime('%Y-%m-%d')
    ws = int((date1 + i - m).strftime('%W')) + 1
    h = h % 2
    if h == 0:
        k += 1
    k = k % len(l1)
    v.append((l1[k][0], l1[k][1], d, ws))
    # print l1[k], l2[h % 6][0], d, l2[h % 6][1], w_dic[w]
    i += m
    h += 1

try:
    conn = MySQLdb.Connect(host='172.22.178.98', user='root', passwd='hadoop', db='ja_hbase', charset='utf8')
    cur = conn.cursor()
    cur.executemany('insert into Duty_Tool_Soft (NAME, PHONE, DATE, WEEKS) values(%s,%s,%s,%s)', v)
    conn.commit()
    cur.close()
    conn.close()
except MySQLdb.Error, e:
    os.system('echo "Mysql Error e.args[0]: e.args[1]"')

