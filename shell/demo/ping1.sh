#!/bin/bash
#检测目标主机的状态
#by tianyun 2015/9/1 v1.0

ping -c1 172.16.8.4 &>/dev/null

if [ $? -eq 0 ];then
	echo -e  "\e[1;32m Host 172.16.8.4 is up. \e[0m"
else
	echo -e  "\e[1;31m Host 172.16.8.4 is down! \e[0m"
fi
