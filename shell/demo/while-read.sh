#!/bin/bash
while read -p "请输入要创建的用户: " user
do
	if [ -z "$user" ];then
		exit 1
	fi	

	useradd $user
	if [ $? -eq 0 ];then
		echo "$user created..."
	fi
done
