#!/bin/bash

bak_ip=172.19.103.25
yum -y install nfs-utils
mkdir -p /mnt/{kvm,qemu}
mount -t nfs $bak_ip:/data0/kvm /mnt/kvm
mount -t nfs $bak_ip:/etc/libvirt/qemu /mnt/qemu
echo "$bak_ip:/etc/libvirt/qemu /mnt/kvm nfs defaults 0 0
$bak_ip:/data0/kvm /mnt/qemu nfs defaults 0 0" >> /etc/fstab
echo "$[$RANDOM % 50 + 5] 0 * * * rsync -lptgoD /data0/kvm/*.qcow2 /mnt/kvm; rsync -lptgoD /etc/libvirt/qemu/*.xml /mnt/kvm" >> /var/spool/cron/root
