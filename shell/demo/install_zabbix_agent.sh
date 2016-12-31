#!/bin/bash
zabbix_server=192.168.122.69
ntp_server=172.16.8.100

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
	zabbix_agent=web`echo $ip |awk -F"." '{print $NF}'`
	ssh $ip "sed -ir "/^HOSTNAME/cHOSTNAME=${zabbix_agent}" /etc/sysconfig/network"
	ssh $ip "wget -q ftp://172.16.8.100/uplooking.repo -P /etc/yum.repos.d"
	ssh $ip "yum -y install zabbix22 zabbix22-agent"
	ssh $ip "sed -ir "s/^Server=.*/Server=${zabbix_server}/" /etc/zabbix_agentd.conf" 
	ssh $ip "sed -ir "s/^ServerActive=.*/ServerActive=${zabbix_server}/" /etc/zabbix_agentd.conf" 
	ssh $ip "sed -ir "s/^Hostname=.*/Hostname=${zabbix_agent}/" /etc/zabbix_agentd.conf" 
	ssh $ip "chkconfig zabbix-agent on"
	ssh $ip "ntpdate -b $ntp_server"
	ssh $ip "echo '*/5 * * * * root ntpdate' $ntpserver > /etc/crontab"
	ssh $ip "iptables -F; service iptables save"
	ssh $ip "sed -ir 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config"
	
	ssh $ip "yum -y install httpd; chkconfig httpd on; service httpd start"
	ssh $ip "reboot"
	}&
done

wait
echo "finish..."

