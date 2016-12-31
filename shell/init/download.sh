#!/bin/bash
mkdir /software/servers -p
cd /software/servers
wget http://172.22.99.122/iso/jdk1.6.0_25.tar.gz
wget http://172.22.99.122/iso/jdk-7u67-linux-x64.tar.gz
wget http://172.22.99.122/iso/lzo.tar.gz
wget http://172.22.99.122/iso/Python-3.2.3.tgz
wget http://172.22.99.122/iso/iftop-1.0-0.7.pre4.el6.x86_64.rpm
server_release=`cat /etc/redhat-release |awk -F "release" '{print $2}'|awk  -F '' '{OFS="";print $2}'`
if [ $server_release == 7 ];then
	wget http://172.22.99.122/iso/gangliarpm_centos7.tar.gz -O /software/servers/gangliarpm.tar.gz
	wget http://172.22.99.122/iso/saltrpm_centos7.tar.gz -O /software/servers/saltrpm.tar.gz
else
	wget http://172.22.99.122/iso/gangliarpm_centos6.tar.gz -O /software/servers/gangliarpm.tar.gz
        wget http://172.22.99.122/iso/saltrpm_centos6.tar.gz -O /software/servers/saltrpm.tar.gz
fi
chown -R hadp.hadp /software/servers
