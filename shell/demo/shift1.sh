#!/bin/bash
#shift1
while [ $# -ne 0 ]  
do
	let sum+=$1
	shift
done
echo "所有数相加的各是: $sum"
