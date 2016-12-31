#!/bin/bash
echo "程序开始"
name=zhuzhu

read -p "请输入正确的名字: " input_name

while :
do
	if [ "$input_name" = "$name" ];then
		break 2
	else
		read -p "输入不正确，请重新的输入: " input_name
	fi
done 

echo "程序的其它部分运行...."
