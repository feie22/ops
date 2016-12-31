#!/bin/bash
while read line
do
	echo $line
done <<< /etc/hosts
#done <<< "$(find . -iname "*.txt")"
