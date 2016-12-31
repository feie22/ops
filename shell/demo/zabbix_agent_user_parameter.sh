#!/bin/bash

for ip in `cat ip.txt`
do
	{
	ssh $ip "echo mem.free,/usr/bin/free \| awk \'/^Mem/{print '\$4'}\' >> /etc/zabbix_agentd.conf"
	ssh $ip "service zabbix-agent restart"
	}&
done

wait
echo "finish..."

