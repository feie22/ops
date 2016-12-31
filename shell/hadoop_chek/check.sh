#!/bin/bash
LANG=zh_CN.UTF-8
CLUSTER_NAME=$1


echo 开始进行$CLUSTER_NAME集群的日常巡检工作

echo info:1.开始检查nn的内核配置
result=`salt -L \`python ~/yangsong/getIP.py $CLUSTER_NAME hadoop-nn1,nn2,nn3,nn4,nn5,nn6,nn7,nn8,nn9,nn10\` cmd.run 'md5sum /etc/sysctl.conf'|grep -v 172|sort|uniq -c|wc -l`
if [ $result -gt 1 ]
then
    echo "error:nn内核配置不一致或个别服务器返回异常"
else
    echo "info:nn内核配置一致"
fi

echo info:2.开始检查其他节点的内核配置
result=`salt -L \`python ~/yangsong/getIP.py $CLUSTER_NAME hadoop-dn,rm,nm,jh1,jh2,jh3,jh4,jh5,jn,balancer,metastore\` cmd.run 'md5sum /etc/sysctl.conf'|grep -v 172|sort|uniq -c|wc -l`
if [ $result -gt 1 ]
then
    echo "error:其他内核配置不一致或个别服务器返回异常"
else
    echo "info:其他内核配置一致"
fi

echo info:3.开始检查所有节点的limits配置文件
result=`salt -L \`python ~/yangsong/getIP.py $CLUSTER_NAME\` cmd.run 'md5sum /etc/security/limits.conf'|grep -v 172|sort|uniq -c|wc -l`
if [ $result -gt 1 ]
then
    echo "error:limits配置不一致或个别服务器返回异常"
else
    echo "info:所有节点limits配置文件一致"
fi

echo info:4.开始检查所有节点的DNS配置文件
result=`salt -L \`python ~/yangsong/getIP.py $CLUSTER_NAME\` cmd.run 'md5sum /etc/resolv.conf'|grep -v 172|sort|uniq -c|wc -l`
if [ $result -gt 1 ]
then
    echo "error:DNS配置不一致或个别服务器返回异常"
else
    echo "info:所有节点DNS配置文件一致"
fi

echo info:5.开始检查所有节点系统日志messages文件
salt -L `python /root/yangsong/getIP.py $CLUSTER_NAME` cmd.run 'cat /var/log/messages |grep -E "fail|error"|grep -v salt-minion' > /tmp/$CLUSTER_NAME/messages.log
result=`cat /tmp/$CLUSTER_NAME/messages.log|grep -v 172|grep -v Minions|wc -l`
if [ $result -gt 1 ]
then
    echo "error:系统日志messages有报错信息或个别服务器返回异常"
else
    echo "info:系统日志messages文件正常"
    \rm -rf /tmp/$CLUSTER_NAME/messages.log
fi

echo info:6.开始检查所有节点系统日志dmesg文件
salt -L `python /root/yangsong/getIP.py $CLUSTER_NAME` cmd.run 'dmesg |grep -E "Error|error"' > /tmp/$CLUSTER_NAME/dmesg.log
result=`cat /tmp/$CLUSTER_NAME/dmesg.log|grep -v "failed with error -22"|grep -v "ERST: Error Record"|grep -v "ACPI Error:"|grep -v 172|grep -v Minions|wc -l`
if [ $result -gt 1 ]
then
    echo "error:系统日志dmesg有报错信息或个别服务器返回异常"
else
    echo "info:系统日志dmesg文件正常"
    \rm -rf /tmp/$CLUSTER_NAME/dmesg.log
fi

echo info:7.开始检查所有节点的平均负载
salt -L `python /root/yangsong/getIP.py $CLUSTER_NAME` cmd.run "uptime|awk -F'average: ' '{print \$2}'| awk -F',' '{if (\$1 >50 && \$2 >50 && \$3 >50){print \$1,\$2,\$3} else {print 1}}'" > /tmp/$CLUSTER_NAME/load.log
result=`cat /tmp/$CLUSTER_NAME/load.log|grep -v 172|sort|uniq|wc -l`
if [ $result -gt 1 ]
then
    echo "error:个别服务器平均负载异常或个别服务器返回异常"
else
    echo "info:所有节点负载正常"
    \rm -rf /tmp/$CLUSTER_NAME/load.log
fi

echo info:8.开始检查所有节点的磁盘使用率
salt -L `python /root/yangsong/getIP.py $CLUSTER_NAME` cmd.run "df -h|grep -E 'data*|/'$|awk '{print \"dir:\"\$6 \" tused:\"\$5}'|grep -E '172.|([9][5-9]|100)%$'" > /tmp/$CLUSTER_NAME/disk.log
result=`cat /tmp/$CLUSTER_NAME/disk.log|grep -v 172|sort|uniq|wc -l`
if [ $result -gt 0 ]
then
    echo -e "error:个别服务器磁盘使用率异常或个别服务器返回异常\n以下为明细"
    grep dir  /tmp/$CLUSTER_NAME/disk.log  -B 1|grep -v '\-\-'
else
    echo "info:所有节点磁盘使用率正常"
    \rm -rf /tmp/$CLUSTER_NAME/disk.log
fi

echo info:9.开始检查所有节点的磁盘inode使用率
salt -L `python /root/yangsong/getIP.py $CLUSTER_NAME` cmd.run "df -i|grep -E 'data*|/'$|awk '{print \"dir:\"\$6 \" tused:\"\$5}'|grep -E '172.|([7-9][0-9]|100)%$'" > /tmp/$CLUSTER_NAME/disk_inode.log
result=`cat /tmp/$CLUSTER_NAME/disk_inode.log|grep -v 172|sort|uniq|wc -l`
if [ $result -gt 0 ]
then
    echo "error:个别服务器磁盘inode使用率异常或个别服务器返回异常"
else
    echo "info:所有节点磁盘inode使用率正常"
    \rm -rf /tmp/$CLUSTER_NAME/disk_inode.log
fi

echo info:10.开始检查所有节点的内存使用率
salt -L `python /root/yangsong/getIP.py $CLUSTER_NAME` cmd.run "free -m|grep "Mem"|awk '{if ((\$3-\$7-\$6)/\$2 > 0.9) {print 0}}'" > /tmp/$CLUSTER_NAME/mem.log
result=`cat /tmp/$CLUSTER_NAME/mem.log|grep -v 172|sort|uniq|wc -l`
if [ $result -gt 0 ]
then
    echo "error:个别服务器内存使用率异常或个别服务器返回异常"
else
    echo "info:所有节点内存使用率正常"
    \rm -rf /tmp/$CLUSTER_NAME/mem.log
fi

echo info:11.开始检查所有节点的swap使用率
salt -L `python /root/yangsong/getIP.py $CLUSTER_NAME` cmd.run "free -m|grep "Swap"|awk '{if (\$3/\$2 > 0.2) {print 0}}'" > /tmp/$CLUSTER_NAME/swap.log
result=`cat /tmp/$CLUSTER_NAME/swap.log|grep -v 172|sort|uniq|wc -l`
if [ $result -gt 0 ]
then
    echo "error:个别服务器swap使用率异常或个别服务器返回异常"
else
    echo "info:所有节点swap使用率正常"
    \rm -rf /tmp/$CLUSTER_NAME/swap.log
fi

echo info:12.开始检查所有节点的网卡带宽制式
salt -L `python /root/yangsong/getIP.py $CLUSTER_NAME ` cmd.run "ethtool \`ifconfig |grep {{ grains.id }} -B 1 |head -1|awk  '{print \$1} '\` " template=jinja > /tmp/$CLUSTER_NAME/ethtool.log
result=`cat /tmp/$CLUSTER_NAME/ethtool.log|grep Speed|awk -F ':' '{print $2}'|awk -F 'M' '{if (\$1 < 1000) {print 0}}'|grep -v 172|sort|uniq|wc -l`
if [ $result -gt 0 ]
then
    echo "error:个别服务器网卡带宽制式异常或返回异常"
else
    echo "info:所有节点网卡带宽制式正常"
    \rm -rf /tmp/$CLUSTER_NAME/ethtool.log
fi

echo info:13.开始检查所有节点的连接数
salt -L `python /root/yangsong/getIP.py $CLUSTER_NAME` cmd.run "netstat -ant|wc -l|awk '{if (\$1 > 30000) {print 0}}'" > /tmp/$CLUSTER_NAME/netstat.log
result=`cat /tmp/$CLUSTER_NAME/netstat.log|grep -v 172|sort|uniq|wc -l`
if [ $result -gt 0 ]
then
    echo "error:个别服务器连接数超过3w异常或返回异常"
else
    echo "info:所有节点连接数正常"
    \rm -rf /tmp/$CLUSTER_NAME/netstat.log
fi

echo info:14.开始检查所有节点的僵尸进程
salt -L `python /root/yangsong/getIP.py $CLUSTER_NAME` cmd.run 'ps -ef|grep defunct|grep -v grep|wc -l' > /tmp/$CLUSTER_NAME/zombie.log
result=`cat /tmp/$CLUSTER_NAME/zombie.log|grep -v 172|sort|uniq|wc -l`
if [ $result -gt 1 ]
then
    echo "error:个别服务器存在僵尸进程或返回异常"
else
    echo "info:所有节点不存在僵尸进程"
    \rm -rf /tmp/$CLUSTER_NAME/netstat.log
fi

echo info:15.开始检查所有节点是否存在坏盘
salt -L `python /root/yangsong/getIP.py $CLUSTER_NAME` cmd.run 'find / -depth  -maxdepth 1 -name data*|xargs -i touch {}/diskcheck' runas=hadp > /tmp/$CLUSTER_NAME/diskcheck.log
salt -L `python /root/yangsong/getIP.py $CLUSTER_NAME` cmd.run 'find / -depth  -maxdepth 1 -name data*|xargs -i \rm {}/diskcheck' >> /tmp/$CLUSTER_NAME/diskcheck.log
result=`cat /tmp/$CLUSTER_NAME/diskcheck.log|grep -v 172|sort|uniq|wc -l`
if [ $result -gt 0 ]
then
    echo "error:个别服务器存在坏盘或返回异常"
    grep -B 1 touch /tmp/$CLUSTER_NAME/diskcheck.log |grep -v '\-\-'| sed 'N;s/:\n//' |awk '{ print $1" "$5}'|sed 's/ `//g'|awk -F '/' '{ print $1"的 /"$2" 磁盘有问题，建议执行 salt -L \""$1"\" cmd.run \"umount /"$2";mount /"$2"\"进行修复"}'
else
    echo "info:所有节点不存在坏盘"
    \rm -rf /tmp/$CLUSTER_NAME/diskcheck.log
fi
salt -L `python /root/yangsong/getIP.py $CLUSTER_NAME` cmd.run 'if [ `grep data /etc/fstab|grep -v "#"|wc -l` -gt `df -h|grep data|wc -l` ];  then echo 0; fi' > /tmp/$CLUSTER_NAME/diskcheck1.log
result1=`cat /tmp/$CLUSTER_NAME/diskcheck1.log|grep -v 172|sort|uniq|wc -l`
#echo $result1

echo info:16.开始检查除metastore外的所有节点hadp用户的bashrc文件
result=`salt -L \`python ~/yangsong/getIP.py $CLUSTER_NAME hadoop-nn1,nn2,nn3,nn4,nn5,nn6,nn7,nn8,nn9,nn10,dn,rm,nm,jh1,jh2,jh3,jh4,jh5,jn,balancer\` cmd.run 'md5sum /home/hadp/.bashrc'|grep -v 172|sort|uniq -c|wc -l`
if [ $result -gt 1 ]
then
    echo "error:hadp用户的bashrc文件不一致或个别服务器返回异常"
else
    echo "info:所有节点hadp用户的bashrc文件一致"
fi

echo info:17.开始检查除metastore外的所有节点yarn用户的bashrc文件
result=`salt -L \`python ~/yangsong/getIP.py $CLUSTER_NAME hadoop-nn1,nn2,nn3,nn4,nn5,nn6,nn7,nn8,nn9,nn10,dn,rm,nm,jh1,jh2,jh3,jh4,jh5,jn,balancer\` cmd.run 'md5sum /home/yarn/.bashrc'|grep -v 172|sort|uniq -c|wc -l`
if [ $result -gt 1 ]
then
    echo "error:yarn用户的bashrc文件不一致或个别服务器返回异常"
else
    echo "info:所有节点yarn用户的bashrc文件一致"
fi

