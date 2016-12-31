#!/bin/bash
exec 7<> /etc/hosts
exec 8<> /etc/sysconfig/network

while read -u 7 line
do
	echo $line
	read -u 8 line2
	echo $line2
done

exec 7<&-
exec 8<&-
