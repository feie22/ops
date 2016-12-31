#!/bin/bash
##install jdk
if [ -d /software/servers ]
then
	:
else
	echo "the software dir is not cunzai"
	echo "the software dir is not cunzai" > /var/log/installhd.log
	exit 0
fi
cd /software/servers
tar -zxvf jdk1.6.0_25.tar.gz
tar -zxvf jdk-7u67-linux-x64.tar.gz 
mkdir softwarebak
mv jdk1.6.0_25.tar.gz softwarebak
mv jdk-7u67-linux-x64.tar.gz softwarebak
##install lzo
tar -zxvf lzo.tar.gz
cd lzo/lzo-2.06
./configure --enable-shared
make&&make install
echo "/usr/local/lib" >/etc/ld.so.conf.d/lzo.conf && /sbin/ldconfig -v
cd ../lzop-1.03
./configure --enable-shared
make&&make install
cd /software/servers
mv lzo.tar.gz softwarebak
##install python
LANG=zh
cd /software/servers
tar -zxvf Python-3.2.3.tgz
cd Python-3.2.3
./configure
make
make install
cd /software/servers
mv Python-3.2.3.tgz softwarebak
##install ganglia salt iftop
cd /software/servers
tar -zxvf gangliarpm.tar.gz 
cd /software/servers/ganglia/
rpm -Uvh *.rpm
cd /software/servers
tar -zxvf saltrpm.tar.gz 
cd /software/servers/salt/
rpm -Uvh *.rpm
cd /software/servers
rpm -ivh iftop-1.0-0.7.pre4.el6.x86_64.rpm
mv gangliarpm.tar.gz saltrpm.tar.gz softwarebak
rm -rf ganglia salt iftop-1.0-0.7.pre4.el6.x86_64.rpm
