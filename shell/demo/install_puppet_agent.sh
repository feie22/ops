#!/bin/bash
ntp_server=172.16.8.100
server=puppet-master.tianyun.com

yum -y install expect
for ip in `cat ip.txt`
do
	{
	/usr/bin/expect <<-YANG
	set timeout 10
	spawn ssh-copy-id -i root@$ip
	expect {
		"yes/no" { send "yes\r"; exp_continue}
		"password:" { send "uplooking\r"};
	}
	expect eof
	YANG
	rsync -va /etc/yum.repos.d/puppet.repo $ip:/etc/yum.repos.d
	rsync -va /etc/hosts $ip:/etc
	ssh $ip "ntpdate -b $ntp_server"
	ssh $ip "echo '*/5 * * * * root ntpdate 172.16.8.100 &>/dev/null' >> /etc/crontab"
	ssh $ip "iptables -F; service iptables save"
	ssh $ip "setenforce 0"
	ssh $ip "sed -ir 's/^SELinux=.*/SELinux=disabled/' /etc/selinux/config"

	ssh $ip "yum -y install puppet"
	ssh $ip "chkconfig puppet on"

	hostname=agent`echo $ip |awk -F"." '{print $NF}'`.tianyun.com
	ssh $ip "sed -ir "/^HOSTNAME/cHOSTNAME=${hostname}" /etc/sysconfig/network"
	ssh $ip "echo runinterval = 60 >> /etc/puppet/puppet.conf"
	ssh $ip "echo server = puppet-master.tianyun.com >> /etc/puppet/puppet.conf"

	ssh $ip "reboot"
	}&
done

wait
echo "finish..."

