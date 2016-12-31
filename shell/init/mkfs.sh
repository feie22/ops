#!/bin/bash
# 分区格式化
fdiskMkfs_1(){
if [ `cat /etc/fstab | grep sdb | wc -l` -gt 0 ]; then
echo '分区已经存在，程序终止！'
exit
fi

if [ -d /data0 ]; then
i=1
n=1
else
i=0
n=0
fi
for dev in `ls /dev/sd? | grep -v sda`; do
devNum=$dev"1"
dir="/data"$i
((i=i+1))

mkdir -p $dir

parted -s $dev mklabel gpt
parted -s $dev mkpart primary 1 100%
mkfs.ext4 -T largefile $devNum &

done

#格式化后重启服务器
wait

sleep 60 

ls -l /dev/disk/by-uuid/ >> /root/setup.log

#i=1
for dev in `ls /dev/sd? | grep -v sda|awk -F"/" '{print $3}'`; do
uuid=`ls -l /dev/disk/by-uuid/|grep $dev|awk '{print $9}'`
dir="/data"$n
((n=n+1))
echo "UUID=$uuid $dir ext4 defaults 1 2">>/etc/fstab
done
mount -a
mkdir -p -m 777 /data0/.trash
}

fdiskMkfs_2(){
if [ `cat /etc/fstab | grep sdb | wc -l` -gt 0 ]; then
echo '分区已经存在，程序终止！'
exit
fi

i=0
for dev in `ls /dev/sd? | grep -v sdm`; do
devNum=$dev"1"
dir="/data"$i
((i=i+1))

mkdir -p $dir

parted -s $dev mklabel gpt
parted -s $dev mkpart primary 1 100%
mkfs.ext4 -T largefile $devNum &

done

#格式化后重启服务器
wait

sleep 60 

ls -l /dev/disk/by-uuid/ >> /root/setup.log

i=0
for dev in `ls /dev/sd? | grep -v sdm|awk -F"/" '{print $3}'`; do
uuid=`ls -l /dev/disk/by-uuid/|grep $dev|awk '{print $9}'`
dir="/data"$i
((i=i+1))
echo "UUID=$uuid $dir ext4 defaults 1 2">>/etc/fstab
done
mount -a
mkdir -p -m 777 /data0/.trash
}
if (ls /dev/sd* |grep sda1 &>/dev/null)
then
   fdiskMkfs_1
else
  fdiskMkfs_2
fi
/bin/rm -rf /tmp/mkfs.sh
