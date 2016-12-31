#!/bin/bash
#for-for
for i in {A..F}
do
	echo -n "$i"
	for j in {1..9}
	do
		if [ $j -eq 5 ];then
			break 1	
		else
			echo -n "$j"
		fi
	done
	echo
done	
echo "finish...."
