#!/bin/bash
#ip_txt.sh
>ip.txt

for i in {2..254}
do
	{ 
	ping -c1 192.168.122.$i &>/dev/null && echo "192.168.122.$i" >> ip.txt 
	}&
done
wait
