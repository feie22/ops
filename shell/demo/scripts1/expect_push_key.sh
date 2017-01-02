#!/bin/bash
for ip in `cat ip.txt`
do
	{
	/usr/bin/expect <<YANG
	set timeout 10
	spawn ssh-copy-id -i root@$ip
	expect {
		"yes/no" { send "yes\r"; exp_continue}
		"password:" { send "uplooking\r"};
	}
	expect eof
YANG
	ssh $ip "ip a s eth0" |grep 'inet ' |awk '{print $2}' |awk -F"/" '{print $1}'
	}&
done

wait
echo "finish..."

