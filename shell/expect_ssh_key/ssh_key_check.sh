#!/bin/bash

for i in `cat $HBASE_HOME/conf/regionservers`
#ip.txt
#192.168.122.52	director1 192.168.122.2
#192.168.122.52	director2 192.168.122.3
#...
do
	{
	ssh hadp@$i 'exit' && echo "$i is good"
	if [[ `echo $?` != 0 ]]; then
		echo "$i is bad"
	fi
	}
done

wait 
echo "所有主机检测完成...."
