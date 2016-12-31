#!/bin/bash

for i in `ps -ef | grep QQ | grep -v grep | awk '{print $2}'`
do 
	kill -9 $i
done
