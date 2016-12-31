#!/bin/bash
#############################
##Author: zhangqiuying@jd.com
##Date: 2016-03-25
##Funtion: create raid10_2 && mkfs
##Update: 2016-03-25
#使用脚本create raid10_2前提条件：1.数据盘为空；2.可以使用MegaRAID工具的厂商
function_precondition(){
#判断数据盘是否为空
data=`df -h| grep "/data"| awk '{print $6}'`

for d in $data
do
    r=`ls $d| grep -v "lost+found"`
    if [ -z $r ];then
        echo "$d is empty!"
    else
        echo "$d is not empty,deny create raid10_2!"
        echo "$d:$r"
        exit 1
    fi
done
#判断厂商
_Vendor=`dmidecode -s system-manufacturer|sed '/^#/d'|awk '{print $1}'`
case $_Vendor in
    "Dell"|"IBM"|"LENOVO")
        echo "$_Vendor allow create raid10_2"
        ;;
    *)
        echo "$_Vendor deny create raid10_2"
        exit 1
        ;;
esac
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
/bin/rm -rf  /data*
}
function_clear_disk

#清理除了系统盘之外的raid
function_clear_raid(){
function_clear_disk
L_list=`$_MegaCli64 -CfgDsply -aALL |grep "Target Id"| awk -F ': ' '{print $3}'|awk -F ')' '{print $1}'| sed -n '2,$p'| uniq`
for L_num in $L_list
do
$_MegaCli64 -CfgLDDel -L${L_num} -a0
wait
done
}
function_clear_raid

##create raid10_2
function_add_raid10_2(){
sleep 10
_DELL_Disk_EID_Num=`$_MegaCli64 -PDlist -aAll | grep 'Enclosure Device ID'|head -1 |awk -F ': ' '{print $2}'`
_DELL_Disk_Array=`$_MegaCli64 -PDlist -aAll |grep -B18 -E "JBOD|Unconfigured\(good\)"| grep 'Slot Number'|awk -F ': ' '{print $2}'|sed s/^/$_DELL_Disk_EID_Num:/g|sed -e ':a;N;$ s/\n/,/g;ba'`
_DELL_Disk_Num=`$_MegaCli64 -PDlist -aAll | grep -B18 -E "JBOD|Unconfigured\(good\)"|grep 'Slot Number'|wc -l`
_DELL_Disk_Array_raid10_2=""
if [ $(($_DELL_Disk_Num%2)) == 0 ];then
    _DELL_Disk_Num_half=$(($_DELL_Disk_Num/2))
    if [ $(($_DELL_Disk_Num_half%2)) == 0 ];then
        for ((i=1,j=2,n=0;i<=${_DELL_Disk_Num_half},j<=${_DELL_Disk_Num_half},n<${_DELL_Disk_Num_half}/2;i=i+2,j=j+2,++n))
        do
            _DELL_Disk_Array_raid10_2_list1=`echo ${_DELL_Disk_Array}|awk -v a="$i" -v b="$j" -F ',' '{print $a","$b}'`
            _Array="-Array"$n[$_DELL_Disk_Array_raid10_2_list1]
            _DELL_Disk_Array_raid10_2_1=$_DELL_Disk_Array_raid10_2_1" "$_Array
            echo $_DELL_Disk_Array_raid10_2_list1
        done
        echo $_DELL_Disk_Array_raid10_2_1
        for ((i=${_DELL_Disk_Num_half}+1,j=${_DELL_Disk_Num_half}+2,n=0;i<=${_DELL_Disk_Num},j<=${_DELL_Disk_Num},n<${_DELL_Disk_Num_half}/2;i=i+2,j=j+2,++n))
        do
            _DELL_Disk_Array_raid10_2_list2=`echo ${_DELL_Disk_Array}|awk -v a="$i" -v b="$j" -F ',' '{print $a","$b}'`
            _Array="-Array"$n[$_DELL_Disk_Array_raid10_2_list2]
            _DELL_Disk_Array_raid10_2_2=$_DELL_Disk_Array_raid10_2_2" "$_Array
            echo $_DELL_Disk_Array_raid10_2_list2
        done
        echo $_DELL_Disk_Array_raid10_2_2
        for ((i=1; i<=$_DELL_Disk_Num; ++i))
        do
            _DELL_Disk_Array_list=`echo $_DELL_Disk_Array|awk -v a="$i" -F ',' '{print $a}'`
            $_MegaCli64 -PDMakeGood -PhysDrv[$_DELL_Disk_Array_list] -Force -a0
        done
        $_MegaCli64 -CfgSpanAdd -r10 $_DELL_Disk_Array_raid10_2_1 -a0
        $_MegaCli64 -CfgSpanAdd -r10 $_DELL_Disk_Array_raid10_2_2 -a0
    else
        echo "DELL_Disk_Num is : $_DELL_Disk_Num not allow create raid10_2!!"
    fi
fi
sleep 30
}
function_add_raid10_2

##格式化硬盘并挂载
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
function_raid10_2mkfs(){
wait
sleep 30
if (ls /dev/sd* |grep sda1 &>/dev/null)
then
    fdiskMkfs_1
else
    fdiskMkfs_2
fi
}
function_raid10_2mkfs
