#!/bin/bash
#ipcheck

ipcheck() {
	ips=(`echo $1 |egrep '([0-9]{1,3}\.){3}[0-9]{1,3}' |tr '.' ' '`)
	#if [ ${ips[0]} -le 255 ] && [ ${ips[1]} -le 255 ] && [ ${ips[2]} -le 255 ] && [ ${ips[3]} -le 255 ];then
	#	echo "$1 is ip."
	#else
	#	echo "$1 isn't ip"
	#fi
	

	for i in ${!ips[@]}
	do
		if [ ${ips[$i]} -gt 255 ]  ;then
			echo "$1 no ip"	
			exit
		fi		
	done
	echo "$1 is ip"
}

ipcheck $1
