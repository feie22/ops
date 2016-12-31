#!/bin/bash
echo "未定义前调用"
f1

f1() {
	echo "hello"
}

echo "定义后调用"
f1
f1
f1
