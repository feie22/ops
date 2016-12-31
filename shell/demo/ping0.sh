#!/bin/bash
#测试指定的主机是否连通
# by tianyun 2015/9/2 v1.0

ip=172.16.8.100

if ping -c1 $ip &>/dev/null;then
	echo "$ip is up."
else
	echo "$ip is down." |tee -a  /root/down_list.txt
fi
