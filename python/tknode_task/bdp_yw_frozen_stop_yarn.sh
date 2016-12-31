#!/bin/bash
ssh yarn@172.22.99.99 "stop-yarn.sh"
if [ $? -ne 0 ];then
    exit 1
fi

/home/autodeploy/task/sendmail.py `echo $0|cut -c 3-` "执行完成" 
