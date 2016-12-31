#!/bin/bash
#函数变量
fun3() {
	echo "函数\$num: $num"
	#num=10
	local num=10
	echo "函数\$num赋值后: $num"
}

num=0
echo "调用函数前，程序\$num值: $num"

fun3

echo "调用函数后，程序\$num值: $num"
