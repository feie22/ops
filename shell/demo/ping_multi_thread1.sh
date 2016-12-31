#!/bin/bash
#多进程
for i in {1..254}
do
	{
	ip=172.16.100.$i
	ping -c1 -W1 $ip &>/dev/null
	if [ $? -eq 0 ];then
		echo "$ip is up."
	else
		echo "$ip is down!"
	fi }&
done
wait
echo "ping test finish..."
