#!/bin/bash

bak_ip=172.19.103.24
local_ip=`ip a | egrep -o 172\.19\.103\.[0-9][0-9]| head -1`

yum -y install nfs-utils
mkdir -p /data0/{kvm,kvm_base,kvm_backup,qemu_backup}
mount -t nfs $bak_ip:/data0/kvm_base /data0/kvm_base
mount -t nfs $bak_ip:/data0/kvm_backup /data0/kvm_backup
mount -t nfs $bak_ip:/data0/qemu_backup /data0/qemu_backup
echo "$bak_ip:/data0/kvm_base /data0/kvm_base nfs defaults 0 0
$bak_ip:/data0/kvm_backup /data0/kvm_backup nfs defaults 0 0
$bak_ip:/data0/qemu_backup /data0/qemu_backup nfs defaults 0 0">> /etc/fstab
echo "$[$RANDOM % 50 + 5] 0 * * * rsync -lptgoD /data0/kvm/*.qcow2 /data0/kvm_backup; rsync -lptgoD /etc/libvirt/qemu/*.xml /data0/qemu_backup" >> /var/spool/cron/root


echo "touch /var/lock/subsys/local
echo never > /sys/kernel/mm/redhat_transparent_hugepage/defrag
echo never > /sys/kernel/mm/redhat_transparent_hugepage/enabled
brctl delif br0 eth1
ifconfig br0 down
brctl delbr br0
brctl addbr br0
brctl addif br0 eth1
ip addr add $local_ip/24 broadcast 172.19.103.255 dev br0
ifconfig br0 up
route del -net 172.19.103.0/24 gw 172.19.103.254
route del default gw 172.19.175.254
route add default gw 172.19.103.254
" > /etc/rc.local
source /etc/rc.local
ping -c 1 -w 1 172.19.103.254