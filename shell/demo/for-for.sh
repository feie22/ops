#!/bin/bash
#for-for
for i in {A..F}
do
	echo -n "$i"
	for j in {1..9}
	do
		echo -n "$j"
	done
	echo
done	
