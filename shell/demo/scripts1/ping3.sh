#!/bin/bash
#检测目标主机的状态
#by tianyun 2015/9/1 v3.0
#ip=172.16.8.4
green="\e[1;32m"
red="\e[1;31m"
reset="\e[0m"

ping -c1 $1 &>/dev/null

if [ $? -eq 0 ];then
	echo -e  "$green Host $1 is up. $reset"
else
	echo -e  "$red Host $1 is down! $reset"
fi
