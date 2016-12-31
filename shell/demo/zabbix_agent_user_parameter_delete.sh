#!/bin/bash

for ip in `cat ip.txt`
do
	{
	ssh $ip "sed -ir '\$d' /etc/zabbix_agentd.conf"
	ssh $ip "service zabbix-agent restart"
	}&
done

wait
echo "finish..."

