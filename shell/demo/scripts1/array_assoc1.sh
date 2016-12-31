#!/bin/bash
#按后缀统计不同类型文件的数量
declare -A files

for i in `find $1`
do
	suffix=${i##*.}
	let files[$suffix]++
done

echo "各种文件的数量分别是:　"
echo "==========================================="
for j in ${!files[@]}
do
	echo "$j的数量是: ${files[$j]}"
done
echo "==========================================="
