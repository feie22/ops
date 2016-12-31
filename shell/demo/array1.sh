#!/bin/bash
#array
books=(php puppet zabbix [20]="bash shell")

echo "books数组元数个数是: ${#books[@]}"

#echo "books数组的第1个元数是: ${books[0]}"

echo "开始遍历数组:"

for i in ${!books[@]}
do
	echo "\${books[$i]}: ${books[$i]}"
done

