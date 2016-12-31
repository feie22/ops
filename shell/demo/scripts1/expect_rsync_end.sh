#!/bin/bash
for ip in `cat ip.txt`
do
	{
	/usr/bin/expect <<YANG
	set timeout 10
	spawn rsync -va /etc/shadow root@$ip:/tmp
	expect {
		"yes/no" { send "yes\r"; exp_continue}
		"password:" { send "uplooking\r"};
	}
	expect eof
YANG
	}&
done

wait
echo "finish..."
