#!/bin/bash
OIFS=$IFS
#IFS=$'\n'
IFS=$"
"

for line in `cat /etc/hosts`
do
	echo $line
	sleep 1
done

echo "finish..."
IFS=$OIFS
