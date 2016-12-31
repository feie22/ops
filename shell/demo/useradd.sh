#!/bin/bash
#批量创建用户
#tianyun 2015/9/2 v1.0

init_pass=123456
read -p "请输入用户的前缀: " prefix
read -p "请输入创建用户的数量: " num

#如果不是数字，退出程序
if [[ ! "$num" =~ ^[0-9]+$ ]];then
	echo "你输入的不是数字，程序退出!"
	exit 1
fi

#创建用户
for i in $(seq -w $num)
do
	{
	user=${prefix}${i}
	useradd $user &>/dev/null && user_create=ok || user_create=fail
	echo "$init_pass" | passwd --stdin $user &>/dev/null && user_pass=ok || user_pass=fail
	if [ "$user_create" = "ok" -a "$user_pass" = "ok" ];then
		echo "$user ok" 
	else
		echo "$user fail"
	fi }&
done
wait
echo "测试完成!!!"
