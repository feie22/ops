#!/bin/bash
#centos6 ganglia 安装命令

wget http://172.22.99.122/iso/gangliarpm_centos6.tar.gz -O /tmp/gangliarpm.tar.gz;cd /tmp && tar -zxvf gangliarpm.tar.gz && cd /tmp/ganglia/;rpm -Uvh *.rpm;cd /tmp;\rm -rf gangliarpm.tar.gz ganglia;chkconfig gmond on;service gmond start