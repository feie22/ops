#!/bin/bash
#jump server
#by tianyun 2015/09/06 v1.0
menu() {
clear
cat <<YANG
====================================================
		跳板主机
		1）mysql1
		2）mysql2
		3）bj-web1
		h) help
		q) exit
====================================================
YANG
}

menu

while :
do
	read -p "请选择要连接的主机[1-3]: " action
	case "$action" in
		1) 
			ssh yang@192.168.122.186
			;;
		2) 
			ssh yang@192.168.122.56
			;;
		3) 
			ssh yang@192.168.122.69
			;;
		h) 
			menu
			;;
		'') 
			:
			;;
		q)
			exit
			;;
		*)
			echo "输入错误..."
	esac
done
