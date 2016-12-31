#!/bin/bash
#'wangdelong'
#


for i in crond  snmpd gmond sshd rsyslog
do
	service $i status
done

salt -L  172.17.38.216,172.17.38.217 cmd.run 'md5sum /etc/sysctl.conf' | grep -v 172| sort | uniq -c | wc -l