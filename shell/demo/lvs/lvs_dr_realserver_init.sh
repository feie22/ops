#!/bin/bash
#LVS_DR_Realserver初始化脚本
IFS=$'\n'
alias sed='sed -c --follow-symlinks'
ntpserver=172.16.8.100
gw=192.168.122.1
vip=192.168.122.100

for line in `cat real_serverip.txt`
#real_serverip.txt
#old_ip		hostname newip
#192.168.122.62	web10 192.168.122.10
#192.168.122.72	web20 192.168.122.20
#192.168.122.82	web20 192.168.122.30
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
	ssh root@$ip "yum -y install lftp tree httpd"
	ssh root@$ip "chkconfig httpd on"
	ssh root@$ip "echo $hostname > /var/www/html/index.html"
	ssh root@$ip "ntpdate -b $ntpserver"
	ssh root@$ip "echo 'echo 1 > /proc/sys/net/ipv4/conf/all/arp_ignore' >> /etc/rc.local"
	ssh root@$ip "echo 'echo 2 > /proc/sys/net/ipv4/conf/all/arp_announce' >> /etc/rc.local"
	ssh root@$ip "echo 'ip addr add dev lo' $vip/32 >> /etc/rc.local"
	ssh root@$ip "reboot"
	}&
done

wait 
echo "所有主机初始化完成...."
