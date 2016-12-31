#!/bin/bash
for i in `cat wukongnn.list`;do
    ssh hadp@$i "sed -i '/white.list.enable/{n; s/true/false/;}' /software/servers/hadoop-2.7.1/etc/hadoop/hdfs-site.xml"
    if [ $? -eq 0 ]; then
        echo "$i 成功关闭白名单" 
    else
        echo "$i 失败关闭白名单"
    fi
done

ssh hadp@172.22.90.101 "hdfs dfsadmin -refreshWhitelists ALL"
if [ $? -eq 0 ]; then
    echo "成功刷新白名单"
else
    echo "失败刷新白名单"
fi
/home/autodeploy/task/sendmail.py `echo $0|cut -c 3-` "执行完成"
