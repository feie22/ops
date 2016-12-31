#!/bin/sh
##############################################
#Author wangdelong@jd.com
#Date  2016
#update 2016-07-11

# 判断系统版本，获取IP地址
yum -y remove salt zero*
server_release=`cat /etc/redhat-release |awk -F "release" '{print $2}'|awk  -F '' '{OFS="";print $2}'`
if [ `grep -w "IPADDR" -q /etc/sysconfig/network-scripts/ifcfg-eth0;echo $?` -eq 0 ]
then
    IP=`grep IPA /etc/sysconfig/network-scripts/ifcfg-eth0 |grep -v ^#|awk -F '=' '{print $2}'`
elif [ `grep -w "IPADDR" -q /etc/sysconfig/network-scripts/ifcfg-eth2;echo $?` -eq 0 ]
then
    IP=`grep IPA /etc/sysconfig/network-scripts/ifcfg-eth2 |grep -v ^#|awk -F '=' '{print $2}'`
else
    IP=`grep IPA /etc/sysconfig/network-scripts/ifcfg-bond1 |grep -v ^#|awk -F '=' '{print $2}'`
fi
# 备份salt-minion
tar -zcf /software/servers/softwarebak/salt-minion-2015.tar.gz /etc/salt &> /dev/null 

#安装salt-minion
if [ $server_release == 7 ];then
    wget http://172.22.99.122/iso/saltrpm_2016.3_centos7.tar.gz -O /tmp/saltrpm.tar.gz > /dev/null
else
    wget http://172.22.99.122/iso/saltrpm_2016.3_centos6.tar.gz -O /tmp/saltrpm.tar.gz > /dev/null
fi
cd /tmp && tar -zxf saltrpm.tar.gz && cd /tmp/salt/
#rpm -Uvh *.rpm
yum -y localinstall *.rpm > /dev/null
cd /tmp
rm -rf saltrpm.tar.gz salt
chkconfig salt-minion on
#salt-minion配置
echo "master:
  - 172.19.185.84
  - 172.22.88.20
random_reauth_delay: 60
id: $IP
tcp_pub_port: 8010
tcp_pull_port: 8011
master_port: 8006">/etc/salt/minion
rm -f /etc/salt/pki/minion/minion_master.pub
service salt-minion restart


