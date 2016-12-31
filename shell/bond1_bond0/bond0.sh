#!/usr/bin/bash
#change bond1 to bond0
#author wangdelong
#date 2016-10-19

cd /etc/sysconfig/network-scripts/ && \
cat ifcfg-bond1 > ifcfg-bond0 && \
sed -i 's/bond1/bond0/' ifcfg-bond0 && \
sed -i 's/bond1/bond0/' ifcfg-eth0 && \
sed -i 's/bond1/bond0/' ifcfg-eth1 && \
echo -e "alias bond0 bonding\noptions bonding mode=0 miimon=100"
>/etc/modprobe.d/bonding.conf && \
mv /etc/sysconfig/network-scripts/ifcfg-bond1 /tmp && \
modprobe -r bonding && modprobe bonding && \
#echo -bond1 >/sys/class/net/bonding_masters && \
service network restart
