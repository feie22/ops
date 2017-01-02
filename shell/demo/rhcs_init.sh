#!/bin/bash
#RHCS初始化脚本
alias sed='sed -c --follow-symlinks'
IFS=$'\n'
ntpserver=172.16.8.100

if [ ! -f ~/.ssh/id_rsa.pub ];then
	echo "请使用ssh-keygen建立密钥！！！"
	exit
fi

yum -y install expect

for line in `cat ip.txt`
#ip.txt
#192.168.122.52	web1.tianyun.com
#192.168.122.62	web2.tianyun.com
#...
do
	{
	ip=`echo $line |awk '{print $1}'`
	hostname=`echo $line |awk '{print $2}'`

	ssh root@$ip 'chkconfig NetworkManager off' 
	ssh root@$ip 'iptables -F; service iptables save' 
	ssh root@$ip "sed -r -i  "s/SELINUX.*/SELINUX=disabled/" /etc/selinux/config"
	ssh root@$ip "sed -r -i  "s/HOSTNAME.*/HOSTNAME=$hostname/" /etc/sysconfig/network"
	rsync -va ip.txt $ip:/tmp
	ssh root@$ip "cat /tmp/ip.txt >> /etc/hosts"
	ssh root@$ip "wget ftp://172.16.80.1/rhel6.repo -P /etc/yum.repos.d/"
	ssh root@$ip "yum -y install lftp tree httpd ricci nfs-utils"
	ssh root@$ip "chkconfig ricci on"
	ssh root@$ip "echo 123456 |passwd --stdin ricci"
	ssh root@$ip "ntpdate -b $ntpserver"
	ssh root@$ip "echo '5/* * * * * root ntpdate' $ntpserver > /etc/crontab"
	ssh root@$ip "reboot"
	}&
done

wait 
echo "所有主机初始化完成...."
