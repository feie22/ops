#!/bin/bash
#RHCS初始化脚本
alias sed='sed -c --follow-symlinks'
IFS=$'\n'
ntpserver=172.16.8.100
gw=192.168.122.1

for line in `cat ip.txt`
#ip.txt
#192.168.122.52	director1 192.168.122.2
#192.168.122.52	director2 192.168.122.3
#...
do
	{
	ip=`echo $line |awk '{print $1}'`
	hostname=`echo $line |awk '{print $2}'`
	newip=`echo $line |awk '{print $3}'`

	ssh root@$ip 'chkconfig NetworkManager off' 
	ssh root@$ip 'iptables -F; service iptables save' 
	ssh root@$ip "sed -r -i  "/^SELINUX/cSELINUX=disabled" /etc/selinux/config"
	ssh root@$ip "sed -r -i  "/^HOSTNAME/cHOSTNAME=$hostname" /etc/sysconfig/network"
	ssh root@$ip "sed -r -i  "/^BOOTPROTO/cBOOTPROTO=none" /etc/sysconfig/network-scripts/ifcfg-eth0"
	ssh root@$ip "sed -r -i  "3aIPADDR=$newip" /etc/sysconfig/network-scripts/ifcfg-eth0"
	ssh root@$ip "sed -r -i  "3aPREFIX=24" /etc/sysconfig/network-scripts/ifcfg-eth0"
	ssh root@$ip "sed -r -i  "3aGATEWAY=$gw" /etc/sysconfig/network-scripts/ifcfg-eth0"

	ssh root@$ip "wget ftp://172.16.8.100/rhel6.repo -O /etc/yum.repos.d/rhel6.repo"
	ssh root@$ip "yum -y install ipvsadm keepalived"
	ssh root@$ip "ntpdate -b $ntpserver"
	ssh root@$ip "reboot"
	}&
done

wait 
echo "所有主机初始化完成...."
