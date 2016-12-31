#!/bin/bash

(while true; do
	a=`ifconfig | grep -A 4 eth0|grep drop|awk '{print $4}'| awk -F: '{print $2}'`
	sleep 3
	b=`ifconfig | grep -A 4 eth0|grep drop|awk '{print $4}'| awk -F: '{print $2}'`
	if [[ a -ne b  ]];then
		echo "$a -- $b -- `date`" >> /tmp/dropped.log 
		# echo "$a -- $b -- `date`"
	fi

done) &