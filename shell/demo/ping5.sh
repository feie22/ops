#!/bin/bash
#测试某网段的所有主机
#tianyun 2015/9/2 v1.0

>down_list.txt
network=172.16.100

for ip in {1..254}
do
	{
	ping -c2 -W1 -i.1 ${network}.${ip} &>/dev/null
	if [ $? -eq 0 ];then
		echo "${network}.${ip} is up." 
	else
		echo "${network}.${ip} is down!!!"  >> down_list.txt
	fi }&
done

wait

echo "ping测试完成!!!"
