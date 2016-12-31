#!/bin/bash
#############################
##Author: zhangqiuying@jd.com
##Date: 2016-03-25
##Funtion: create raid0 && mkfs
##Update: 2016-03-25
#使用脚本create raid0前提条件：1.数据盘为空；2.可以使用MegaRAID工具的厂商
#add mkfs_a,mkfs_m function by fanshiyi 2016-08-10
function_precondition(){
#判断数据盘是否为空
#data=`df -h| grep "/data"| awk '{print $6}'`

#for d in $data
#do
#    r=`ls $d| grep -v "lost+found"`
#    if [ -z $r ];then
#        echo "$d is empty!"
#    else
#        echo "$d is not empty,deny create raid10!"
#        echo "$d:$r"
#        exit 1
#    fi
#done
#判断厂商
_Vendor=`dmidecode -s system-manufacturer|sed '/^#/d'|awk '{print $1}'`
case $_Vendor in
    "Dell"|"IBM"|"LENOVO"|"Huawei")
        echo "$_Vendor allow create raid0"
        ;;
    *)
        echo "only 'Dell|IMB|LENOVE|Huawei' is suit,$_Vendor not supported"
#        exit 1
        ;;
esac
#判断是否有进程占用/data*
if (`df -h |grep data` &>/dev/null)
    then
        for dir in `df -h| grep "/data"| awk '{print $6}'`
            do
                if (`lsof $dir` &>/dev/null)
                    then
                        echo "$dir is used by some processes,please check!!!"
                        exit 1
                fi
            done
fi
}
function_precondition

#安装工具MegaRAID
if [ -f /opt/MegaRAID/MegaCli/MegaCli64 ];then
        _MegaCli64='/opt/MegaRAID/MegaCli/MegaCli64'
else
        which MegaCli64 &> /dev/null
        if [ $? -eq 0 ];then
                echo "MegaCli64 already installed!"
        else
                wget http://172.22.99.122/iso/MegaCli-8.07.14-1.noarch.rpm
                rpm -ivh MegaCli-8.07.14-1.noarch.rpm
                /bin/rm MegaCli-8.07.14-1.noarch.rpm
        fi
        _MegaCli64=`which MegaCli64`
fi
#卸载数据盘并删除目录
function_clear_disk(){
_Disk_Num=`df -h| grep data | wc -l`
for ((i=0; i<$_Disk_Num;i++))
do
    umount /data$i
    /bin/rm -rf  /data$i
done
sed -i '/data/d' /etc/fstab
#/bin/rm -rf  /data*
}
function_clear_disk

#清理除了系统盘之外的raid
function_clear_raid(){
#function_clear_disk
L_list=`$_MegaCli64 -CfgDsply -aALL |grep "Target Id"| awk -F ': ' '{print $3}'|awk -F ')' '{print $1}'| sed -n '2,$p'| uniq`
for L_num in $L_list
do
$_MegaCli64 -CfgLDDel -L${L_num} -force -a0
wait
done
}
function_clear_raid
##create raid0
function_add_raid0(){
sleep 5
_DELL_Disk_EID_Num=`$_MegaCli64 -PDlist -aAll | grep 'Enclosure Device ID'|head -1 |awk -F ': ' '{print $2}'`
_DELL_Disk_Array=`$_MegaCli64 -PDlist -aAll |grep -B18 -E "JBOD|Unconfigured\(good\)"| grep 'Slot Number'|awk -F ': ' '{print $2}'|sed s/^/$_DELL_Disk_EID_Num:/g|sed -e ':a;N;$ s/\n/,/g;ba'`
_DELL_Disk_Num=`$_MegaCli64 -PDlist -aAll | grep -B18 -E "JBOD|Unconfigured\(good\)"|grep 'Slot Number'|wc -l`
for ((i=1; i<=$_DELL_Disk_Num; ++i))
do
    _DELL_Disk_Array_list=`echo $_DELL_Disk_Array|awk -v a="$i" -F ',' '{print $a}'`
    $_MegaCli64 -PDMakeGood -PhysDrv[$_DELL_Disk_Array_list] -Force -a0
    $_MegaCli64 -CfgLdAdd -r0 [$_DELL_Disk_Array_list]  -a0
#add wait
    wait
done
}
function_add_raid0

##格式化硬盘并挂载
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

sleep 100

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
#reboot
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

sleep 100

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
#reboot
}
mkfs_a(){
#如果sda存在/data0分区，则对分区格式化并挂载
if (`lsblk -l |grep sda[0-9]|grep -v boot |grep -vw / |grep -vi swap &>/dev/null`)
    then
        a_parts=(`ls /dev/sda[0-9]`)
        data0_part=${a_parts[`expr ${#a_parts[*]}-1`]}
        mkfs.ext4 -T largefile $data0_part &
        wait
        mkdir /data0
        data0_uuid=`blkid -o export $data0_part|head -n1`
        echo "$data0_uuid /data0 ext4 defaults 1 2">>/etc/fstab
        i=1
        j=1
else
        i=0
        j=0
fi

for dev in `ls /dev/sd? | grep -v sda`; do
devNum=$dev"1"
dir="/data"$i
((i=i+1))

mkdir -p $dir

parted -s $dev mklabel gpt
parted -s $dev mkpart primary 1 100%
mkfs.ext4 -T largefile $devNum  & eval pid$i=\$!
#后台并行执行并获取mkfs.ext4的pid
pidlist[$i]=$(eval echo \$pid$i)
done
#wait $(eval echo \$pid$i)
#等待mkfs.ext4的pid结束
while (ps -p ${pidlist[*]} |grep -v PID &>/dev/null)
do
    wait
    sleep 1
done



for dev in `ls /dev/sd? | grep -v sda|awk -F"/" '{print $3}'`; do
uuid=`ls -l /dev/disk/by-uuid/|grep $dev|awk '{print $9}'`
dir="/data"$j
((j=j+1))
echo "UUID=$uuid $dir ext4 defaults 1 2">>/etc/fstab
done
mount -a
mkdir -p -m 777 /data0/.trash

}
mkfs_m(){

i=0
for dev in `ls /dev/sd? | grep -v sdm`; do
devNum=$dev"1"
dir="/data"$i
((i=i+1))

mkdir -p $dir

parted -s $dev mklabel gpt
parted -s $dev mkpart primary 1 100%
mkfs.ext4 -T largefile $devNum & eval pid$i=\$!
pidlist[$i]=$(eval echo \$pid$i)
#wait $(eval echo \$pid$i)
done
while (ps -p ${pidlist[*]} |grep -v PID &>/dev/null)
do
    wait
    sleep 1
done




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

function_raid0mkfs(){
wait
sleep 30
#if (ls /dev/sd* |grep sda1 &>/dev/null)
#优化判断条件
if (`mount |grep -w /|grep sda &>/dev/null`)
then
    fdiskMkfs_1
else
    fdiskMkfs_2
fi
}
#function_raid0mkfs
f_mkfs(){
if (`mount |grep -w /|grep sda &>/dev/null`)
then
    mkfs_a
else
    mkfs_m
fi
}
f_mkfs
