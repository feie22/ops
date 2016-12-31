#!/bin/bash
tmp_fifofile=/tmp/$$.fifo
mkfifo $tmp_fifofile
exec 9<> $tmp_fifofile
rm $tmp_fifofile

thread=10

for i in `seq $thread`
do
	echo >&9
done 

for j in {1..254}
do
	read -u 9
	{
		ip=172.16.100.$j
		ping -c1 -W1 $ip &>/dev/null
		if [ $? -eq 0 ];then
			echo "$ip is up."
		else
			echo "$ip is down."
		fi
		echo >&9
	 }&
done

wait
exec 9>&-
echo "ping test finish..."
