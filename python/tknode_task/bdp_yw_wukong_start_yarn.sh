#!/bin/bash
ssh yarn@172.22.90.129 "start-yarn.sh"
if [ $? -ne 0 ];then
    exit 1
fi

/home/autodeploy/task/sendmail.py `echo $0|cut -c 3-` "执行完成" 
