#!/bin/bash
>ip.txt
>/root/.ssh/known_hosts

if [ ! -f ~/.ssh/id_rsa.pub ];then
        echo "请使用ssh-keygen建立密钥！！！"
        exit
fi
yum -y install expect

for i in {2..254}
do
	{
	ip=192.168.122.$i
	ping -c1 -W1 $ip &>/dev/null
	if [ $? -eq 0 ];then
		echo $ip >> ip.txt
		/usr/bin/expect <<-EOF
		set timeout 10
		spawn ssh-copy-id -i $ip
		expect {
			"*yes/no" { send "yes\r"; exp_continue}
			"*password:" { send "uplooking\r" }
		}

		expect "#"
		send "exit\r"
		expect eof
		EOF
	fi
	}&
done

wait 
echo "finish...."


