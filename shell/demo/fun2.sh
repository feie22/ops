#!/bin/bash
#函数参数

fun2() {
	echo "函数的第一个位置参数: $1"
	echo "函数的第二个位置参数: $2"
	echo "变量abc: $abc"
}

abc=9999
echo "程序的第一个位置参数: $1"
echo "程序的第二个位置参数: $2"
echo "================================"
#fun2 a b 
fun2 $1 $2