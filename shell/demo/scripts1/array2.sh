#!/bin/bash
#通过文件定义组数
i=0
while read line
do
	grub[$i]=$line
	let i++
done < /etc/grub.conf

echo "通过索引遍历数组: "
for i in ${!grub[@]} 
do
	echo "\${grub[$i]}: ${grub[$i]}"
done
