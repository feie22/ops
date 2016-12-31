#!/bin/bash
if [ $# -eq 0 ];then
	echo "Usage: `basename $0` par1"
	exit 1
fi

if [ ! -f "$1" ];then
	echo "error file!"
	exit 2
fi

for ip in `cat $1`
do
	ping -c1 -W1 $ip &>/dev/null
	if [ $? -eq 0 ];then
		echo "$ip is up."
	else
		echo "$ip is down."
	fi
done
