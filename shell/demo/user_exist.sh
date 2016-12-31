#!/bin/bash
id alice &>/dev/null

if [ $? -eq 0 ];then
	echo "exist"
fi
