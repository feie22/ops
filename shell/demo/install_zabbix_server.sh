#!/bin/bash
#install zabbix server
#by tianyun v1.0 2015/10/12
ntp_server=172.16.8.100
#zabbix_pass=tianyun
zabbix_sql=/usr/share/zabbix-mysql
DBSocket=/var/lib/mysql/mysql.sock

system_init() {
	iptables -F
	service iptables save
	setenforce 0
	sed -ri 's/^SELINUX=.*/SELINUX=disabled/' /etc/selinux/config	
	service NetworkManager stop
	chkconfig NetworkManager off
	ntpdate -b $ntp_server
	echo "*/5 * * * * root ntpdate $ntp_server &>/dev/null" >> /etc/crontab
}

install_zabbix_server() {
	yum -y install zabbix22 zabbix22-server \
	zabbix22-web zabbix22-web-mysql \
	zabbix22-agent mysql-server
	sed -ri '/\[mysqld\]/acharacter-set-server=utf8' /etc/my.cnf
	sed -ri '/\[mysqld\]/ainnodb_file_per_table=1' /etc/my.cnf
	chkconfig mysqld on
	service mysqld start
	
	mysql -e "create database zabbix character set utf8"
	mysql -e "grant all privileges on zabbix.* to zabbix@localhost identified by 'tianyun'"	
	mysql -e 'flush privileges'

	echo "正在导入表结构,请稍候..."
	mysql -uzabbix -ptianyun zabbix < $zabbix_sql/schema.sql
	mysql -uzabbix -ptianyun zabbix < $zabbix_sql/images.sql
	mysql -uzabbix -ptianyun zabbix < $zabbix_sql/data.sql
	
	#zabbix_server.conf
	sed -ric --follow-symlinks '/DBHost=/aDBHost=localhost' /etc/zabbix_server.conf
	sed -ri '/DBPassword=/aDBPassword=tianyun' /etc/zabbix_server.conf
	
	service zabbix-server restart
	chkconfig zabbix-server on 	
	
	#/etc/httpd/conf.d/zabbix.conf
	sed -ri '/AllowOverride/aphp_value max_execution_time 300\
	php_value memory_limit 128M \
	php_value post_max_size 16M \
	php_value upload_max_filesize 2M \
	php_value max_input_time 300 \
	php_value date.timezone Asia/Shanghai' /etc/httpd/conf.d/zabbix.conf

	service httpd restart
	chkconfig httpd on

	clear
	cat <<-EOF
	+--------------------------------------------------------------------+
	|			http://localhost/zabbix			     |
	+--------------------------------------------------------------------+
	EOF
}

system_init
install_zabbix_server
