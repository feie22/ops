#!/bin/bash
#for-for
for i in {A..F}
do
	echo -n "$i"
	for j in {1..9}
	do
		if [ $j -eq 5 ];then
			continue
		fi
		echo -n "$j"
	done
	echo
done	
echo "finish...."
