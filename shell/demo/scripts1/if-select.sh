#!/bin/bash
#启动停止sshd服务
if [ "$1" = "start" ];then
	/etc/init.d/sshd start
elif [ "$1" = "stop" ];then
	/etc/init.d/sshd stop
elif [ "$1" = "restart" ];then
	/etc/init.d/sshd restart
elif [ "$1" = "reload" ];then
	/etc/init.d/sshd reload
else
	echo "Usage: `basename $0` {start|stop|restart|reload|force-reload|condrestart|try-restart|status}"	
fi
