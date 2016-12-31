#!/bin/bash
#system manager
#by tianyun 2015/09/06 v1.0
menu() {
clear
cat <<YANG
+----------------------------------------+
|	1) 查看磁盘分区			 |
|	2) 查看内存
|	3) 查看系统负载
|	q) 退出程序			 |
+----------------------------------------+
YANG
}

menu


while :
do
	
	read -p "请选择相应的操作[1-3], h帮助: " action
	case "$action" in
		1)
			xxx
			;;
		2)
			yyy
			;;
		3)	uptime;;
		'')
			:
			;;
		h)
			menu
			;;
		q)
			exit
			;;
		*)	
			echo "选择不正确，请重新输"		
			;;
	esac
done
