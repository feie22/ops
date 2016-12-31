#!/bin/bash
#返回值
f4() {
	[ -f /etc/hosts ]
	if [ -f /etc/passwd ];then
		return 0
	fi
	return 1
}

f4
echo "函数的返回值: $?"
