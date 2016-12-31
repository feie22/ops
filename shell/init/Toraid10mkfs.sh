#!/bin/bash
#############################
##Author: zhangqiuying@jd.com
##Date: 2015-12-25
##Funtion: create raid10 && mkfs
##Update: 2016-04-08
#使用脚本create raid10前提条件：1.数据盘为空；2.可以使用MegaRAID工具的厂商
function_precondition(){
#判断数据盘是否为空
data=`df -h| grep "/data"| awk '{print $6}'`

for d in $data
do
    r=`ls $d| grep -v "lost+found"`
    if [ -z $r ];then
        echo "$d is empty!"
    else
        echo "$d is not empty,deny create raid10!"
        echo "$d:$r"
        exit 1
    fi
done
#判断厂商
_Vendor=`dmidecode -s system-manufacturer|sed '/^#/d'|awk '{print $1}'`
case $_Vendor in
    "Huawei"|"Dell"|"IBM"|"LENOVO")
        echo "$_Vendor allow create raid10"
        ;;
    *)
        echo "$_Vendor deny create raid10"
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
##create raid10
function_add_raid10(){
sleep 10
_DELL_Disk_EID_Num=`$_MegaCli64 -PDlist -aAll | grep 'Enclosure Device ID'|head -1 |awk -F ': ' '{print $2}'`
_DELL_Disk_Array=`$_MegaCli64 -PDlist -aAll |grep -B18 -E "JBOD|Unconfigured\(good\)"| grep 'Slot Number'|awk -F ': ' '{print $2}'|sed s/^/$_DELL_Disk_EID_Num:/g|sed -e ':a;N;$ s/\n/,/g;ba'`
_DELL_Disk_Num=`$_MegaCli64 -PDlist -aAll | grep -B18 -E "JBOD|Unconfigured\(good\)"|grep 'Slot Number'|wc -l`
_DELL_Disk_Array_raid10=""
for ((i=1,j=2,n=0; i<=$_DELL_Disk_Num,j<=$_DELL_Disk_Num,n<$_DELL_Disk_Num/2; i=i+2,j=j+2,++n))
do
    _DELL_Disk_Array_raid10_list=`echo $_DELL_Disk_Array|awk -v a="$i" -v b="$j" -F ',' '{print $a","$b}'`
    echo $_DELL_Disk_Array_raid10_list
    _Array="-Array"$n[$_DELL_Disk_Array_raid10_list]
    _DELL_Disk_Array_raid10=$_DELL_Disk_Array_raid10" "$_Array
done
for ((i=1; i<=$_DELL_Disk_Num; ++i))
do
    _DELL_Disk_Array_list=`echo $_DELL_Disk_Array|awk -v a="$i" -F ',' '{print $a}'`
    $_MegaCli64 -PDMakeGood -PhysDrv[$_DELL_Disk_Array_list] -Force -a0
done
$_MegaCli64 -CfgSpanAdd -r10 $_DELL_Disk_Array_raid10 -a0
sleep 30
}
function_add_raid10

##格式化硬盘并挂载
function_mkfs(){
sleep 30
df -h | grep "/dev/sda"
if [ $? -eq 0 ];then
    parted -s /dev/sdb mklabel gpt
    parted -s /dev/sdb mkpart primary 1 100%
    mkfs.ext4 -T largefile /dev/sdb1 &
    wait
    sleep 100
    sed -i '/data/d' /etc/fstab
    echo "UUID=`blkid /dev/sdb1|awk -F'"' '{print $2}'` /data0 ext4 defaults 1 2">>/etc/fstab
else
    parted -s /dev/sda mklabel gpt
    parted -s /dev/sda mkpart primary 1 100%
    mkfs.ext4 -T largefile /dev/sda1 &
    wait
    sleep 100
    sed -i '/data/d' /etc/fstab
    echo "UUID=`blkid /dev/sda1|awk -F'"' '{print $2}'` /data0 ext4 defaults 1 2">>/etc/fstab
fi
mkdir /data0
mount -a
mkdir -p -m 777 /data0/.trash
}
function_mkfs
