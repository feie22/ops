#!/bin/bash
#通过关联数组统计/etc/passwd中不同类型shell的数量
declare -A shells

while read line
do
	#shell_type=${line##*:}
	shell_type=`echo $line |awk -F: '{print $7}'`
	let shells[$shell_type]++
done < /etc/passwd

echo "各种shell的数量分别是:　"
echo "==========================================="
for i in ${!shells[@]}
do
	echo "$i的数量是: ${shells[$i]}"
done
echo "==========================================="
