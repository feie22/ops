#!/bin/bash
#启动/停止sshd
#by tianyun 2015/09 v1.0
case "$1" in
	start)
		/etc/init.d/sshd start		
		;;
	stop)
		/etc/init.d/sshd stop
		;;
	restart)
		/etc/init.d/sshd stop
		/etc/init.d/sshd start
		;;
	*)
		echo "Usage: `basename $0` {start|stop|restart|reload|force-reload|condrestart|try-restart|status}"
esac
