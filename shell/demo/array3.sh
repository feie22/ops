#!/bin/bash
#通过文件定义数组
exec 6<> /etc/hosts

while read -u 6 line
do
	hosts+=("$line")
done 

exec 6<&-

echo "通过索引遍历数组: "
for i in ${!hosts[@]}
do
	echo "\${hosts[$i]}: ${hosts[$i]}"
done
