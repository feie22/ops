#!/bin/bash
#auto gateway
gw1=172.16.100.128
gw2=172.16.100.199

while :
do
	ip r del
	ip r add default via $gw1 	
	while ping -c1 $gw1 &>/dev/null
	do
		sleep 2
	done


	ip r del
	ip r add default via $gw2
	while ping -c1 $gw2 &>/dev/null
	do
		sleep 2
	done
done &
