#!/bin/bash
#使用脚本create raid前提条件：1.数据盘为空；2.可以使用MegaRAID工具的厂商
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
    "Dell"|"IBM"|"LENOVO")
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
if [ ! -f /opt/MegaRAID/MegaCli/MegaCli64 ]
then
    wget http://172.22.99.122/iso/MegaCli-8.07.14-1.noarch.rpm
    rpm -ivh MegaCli-8.07.14-1.noarch.rpm
    /bin/rm MegaCli-8.07.14-1.noarch.rpm
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
/bin/rm -rf /data*
}
#获得硬盘信息
_DELL_Disk_EID_Num=`/opt/MegaRAID/MegaCli/MegaCli64 -PDlist -aAll | grep 'Enclosure Device ID'|head -1 |awk -F ': ' '{print $2}'`
_DELL_Disk_Array=`/opt/MegaRAID/MegaCli/MegaCli64 -PDlist -aAll |grep -B18 -E "JBOD|Unconfigured\(good\)"| grep 'Slot Number'|awk -F ': ' '{print $2}'|sed s/^/$_DELL_Disk_EID_Num:/g|sed -e ':a;N;$ s/\n/,/g;ba'`
echo $_DELL_Disk_Array
_DELL_Disk_Num=`/opt/MegaRAID/MegaCli/MegaCli64 -PDlist -aAll | grep -B18 -E "JBOD|Unconfigured\(good\)"|grep 'Slot Number'|wc -l`

function_status_raid(){
/opt/MegaRAID/MegaCli/MegaCli64 -CfgDsply -aALL |grep -E "DISK\ GROUP|Slot\ Number|RAID\ Level|Target|Raw\ Size"
}
function_status_disk(){
/opt/MegaRAID/MegaCli/MegaCli64 -PDlist -aALL  | grep -E "DISK\ GROUP|Slot\ Number|postion:|Firmware\ state:"
}
#将磁盘改成JBOD模式
function_make_jbod(){
for ((i=1; i<=$_DELL_Disk_Num; ++i))
do
    _DELL_Disk_Array_list=`echo $_DELL_Disk_Array|awk -v a="$i" -F ',' '{print $a}'`
    /opt/MegaRAID/MegaCli/MegaCli64 -PDMakeJBOD -PhysDrv[$_DELL_Disk_Array_list] -a0
done
}
function_add_raid10(){
sleep 10
_DELL_Disk_EID_Num=`/opt/MegaRAID/MegaCli/MegaCli64 -PDlist -aAll | grep 'Enclosure Device ID'|head -1 |awk -F ': ' '{print $2}'`
_DELL_Disk_Array=`/opt/MegaRAID/MegaCli/MegaCli64 -PDlist -aAll |grep -B18 -E "JBOD|Unconfigured\(good\)"| grep 'Slot Number'|awk -F ': ' '{print $2}'|sed s/^/$_DELL_Disk_EID_Num:/g|sed -e ':a;N;$ s/\n/,/g;ba'`
_DELL_Disk_Num=`/opt/MegaRAID/MegaCli/MegaCli64 -PDlist -aAll | grep -B18 -E "JBOD|Unconfigured\(good\)"|grep 'Slot Number'|wc -l`
_DELL_Disk_Array_raid10=""
for ((i=1,j=2,n=0; i<=$_DELL_Disk_Num,j<=$_DELL_Disk_Num,n<$_DELL_Disk_Num/2; i=i+2,j=j+2,++n))
do
    _DELL_Disk_Array_raid10_list=`echo $_DELL_Disk_Array|awk -v a="$i" -v b="$j" -F ',' '{print $a,$b}'`
    echo $_DELL_Disk_Array_raid10_list
    _Array="-Array"$n[$_DELL_Disk_Array_raid10_list]
    _DELL_Disk_Array_raid10=$_DELL_Disk_Array_raid10" "$_Array
done
for ((i=1; i<=$_DELL_Disk_Num; ++i))
do
    _DELL_Disk_Array_list=`echo $_DELL_Disk_Array|awk -v a="$i" -F ',' '{print $a}'`
    /opt/MegaRAID/MegaCli/MegaCli64 -PDMakeGood -PhysDrv[$_DELL_Disk_Array_list] -Force -a0
done
/opt/MegaRAID/MegaCli/MegaCli64 -CfgSpanAdd -r10 $_DELL_Disk_Array_raid10 -a0
sleep 30
}

function_add_raid50(){
sleep 10
_DELL_Disk_EID_Num=`/opt/MegaRAID/MegaCli/MegaCli64 -PDlist -aAll | grep 'Enclosure Device ID'|head -1 |awk -F ': ' '{print $2}'`
_DELL_Disk_Array=`/opt/MegaRAID/MegaCli/MegaCli64 -PDlist -aAll |grep -B18 -E "JBOD|Unconfigured\(good\)"| grep 'Slot Number'|awk -F ': ' '{print $2}'|sed s/^/$_DELL_Disk_EID_Num:/g|sed -e ':a;N;$ s/\n/,/g;ba'`
_DELL_Disk_Num=`/opt/MegaRAID/MegaCli/MegaCli64 -PDlist -aAll | grep -B18 -E "JBOD|Unconfigured\(good\)"|grep 'Slot Number'|wc -l`
_DELL_Disk_Array_raid50=""
for ((i=1,j=2,m=3,n=0; i<=$_DELL_Disk_Num,j<=$_DELL_Disk_Num,m<=$_DELL_Disk_Num,n<$_DELL_Disk_Num/3; i=i+3,j=j+3,m=m+3,++n))
do
    _DELL_Disk_Array_raid50_list=`echo $_DELL_Disk_Array|awk -v a="$i" -v b="$j" -v c="$m" -F ',' '{print $a,$b,$c}'`
    echo $_DELL_Disk_Array_raid50_list
    _Array="-Array"$n[$_DELL_Disk_Array_raid50_list]
    _DELL_Disk_Array_raid50=$_DELL_Disk_Array_raid50" "$_Array
done
for ((i=1; i<=$_DELL_Disk_Num; ++i))
do
    _DELL_Disk_Array_list=`echo $_DELL_Disk_Array|awk -v a="$i" -F ',' '{print $a}'`
    /opt/MegaRAID/MegaCli/MegaCli64 -PDMakeGood -PhysDrv[$_DELL_Disk_Array_list] -Force -a0
done
/opt/MegaRAID/MegaCli/MegaCli64 -CfgSpanAdd -r50 $_DELL_Disk_Array_raid50 -a0
sleep 30
}

function_add_raid5(){
sleep 10
_DELL_Disk_EID_Num=`/opt/MegaRAID/MegaCli/MegaCli64 -PDlist -aAll | grep 'Enclosure Device ID'|head -1 |awk -F ': ' '{print $2}'`
_DELL_Disk_Array=`/opt/MegaRAID/MegaCli/MegaCli64 -PDlist -aAll |grep -B18 -E "JBOD|Unconfigured\(good\)"| grep 'Slot Number'|awk -F ': ' '{print $2}'|sed s/^/$_DELL_Disk_EID_Num:/g|sed -e ':a;N;$ s/\n/,/g;ba'`
_DELL_Disk_Num=`/opt/MegaRAID/MegaCli/MegaCli64 -PDlist -aAll | grep -B18 -E "JBOD|Unconfigured\(good\)"|grep 'Slot Number'|wc -l`
_DELL_Disk_Array_raid5=[${_DELL_Disk_Array}]
for ((i=1; i<=$_DELL_Disk_Num; ++i))
do
    _DELL_Disk_Array_list=`echo $_DELL_Disk_Array|awk -v a="$i" -F ',' '{print $a}'`
    /opt/MegaRAID/MegaCli/MegaCli64 -PDMakeGood -PhysDrv[$_DELL_Disk_Array_list] -Force -a0
done
/opt/MegaRAID/MegaCli/MegaCli64 -CfgLdAdd -r5 $_DELL_Disk_Array_raid5  -a0
sleep 30
}
function_add_raid0(){
#_DELL_Disk_Array_raid0=[${_DELL_Disk_Array}]
sleep 5
_DELL_Disk_EID_Num=`/opt/MegaRAID/MegaCli/MegaCli64 -PDlist -aAll | grep 'Enclosure Device ID'|head -1 |awk -F ': ' '{print $2}'`
_DELL_Disk_Array=`/opt/MegaRAID/MegaCli/MegaCli64 -PDlist -aAll |grep -B18 -E "JBOD|Unconfigured\(good\)"| grep 'Slot Number'|awk -F ': ' '{print $2}'|sed s/^/$_DELL_Disk_EID_Num:/g|sed -e ':a;N;$ s/\n/,/g;ba'`
_DELL_Disk_Num=`/opt/MegaRAID/MegaCli/MegaCli64 -PDlist -aAll | grep -B18 -E "JBOD|Unconfigured\(good\)"|grep 'Slot Number'|wc -l`
for ((i=1; i<=$_DELL_Disk_Num; ++i))
do
    _DELL_Disk_Array_list=`echo $_DELL_Disk_Array|awk -v a="$i" -F ',' '{print $a}'`
    /opt/MegaRAID/MegaCli/MegaCli64 -PDMakeGood -PhysDrv[$_DELL_Disk_Array_list] -Force -a0
    /opt/MegaRAID/MegaCli/MegaCli64 -CfgLdAdd -r0 [$_DELL_Disk_Array_list]  -a0
done
}
#格式化硬盘并挂载
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
function_noraidmkfs(){
function_make_jbod
wait
sleep 30
if (ls /dev/sd* |grep sda1 &>/dev/null)
then
    fdiskMkfs_1
else
    fdiskMkfs_2
fi
}
function_raid0mkfs(){
wait
sleep 30
if (ls /dev/sd* |grep sda1 &>/dev/null)
then
    fdiskMkfs_1
else
    fdiskMkfs_2
fi
}
#只清除数据盘所做的raid
function_clear_raid(){
function_clear_disk
L_list=`/opt/MegaRAID/MegaCli/MegaCli64 -CfgDsply -aALL |grep "Target Id"| awk -F ': ' '{print $3}'|awk -F ')' '{print $1}'| sed -n '2,$p'| uniq`
for L_num in $L_list
do
/opt/MegaRAID/MegaCli/MegaCli64 -CfgLDDel -L${L_num} -a0
wait
done
}
case $1 in
    raidstatus)
        function_status_raid
        ;;
    diskstatus)
        function_status_disk
        ;;
    raid10)
        function_add_raid10
        ;;
    raid50)
        function_add_raid50
        ;;
    raid5)
        function_add_raid5
        ;;
    raid0)
        function_add_raid0
        ;;
    raid10mkfs)
        function_clear_disk
#        /bin/rm -rf /data*
        function_clear_raid
        function_add_raid10
        function_mkfs
        ;;
    raid50mkfs)
        function_clear_disk
        function_clear_raid
        function_add_raid50
        function_mkfs
        ;;
    raid5mkfs)
        function_clear_disk
        function_add_raid5
        function_mkfs
        ;;
    raid0mkfs)
        function_clear_disk
        function_add_raid0
        function_raid0mkfs
        ;;
    raid_clear)
        function_clear_raid
        ;;
    disk_clear)
        function_clear_disk
        ;;
    mkfs)
        function_mkfs
        ;;
    mkjbod)
        function_make_jbod
        ;;
    mkfs_noraid)
        function_noraidmkfs
        ;;
    mkfs_raid0)
        function_raid0mkfs
        ;;
    *)
        echo "--------------------------------"
        echo "Usage:$0 {raidstatus|diskstatus|raid10|raid50|raid5|raid0|raid10mkfs|raid50mkfs|raid5mkfs|raid0mkfs|raid_clear|disk_clear|mkfs|mkjbod|mkfs_noraid|mkfs_raid0}"
        echo "--------------------------------" 
        ;;
esac
#/bin/rm $0
exit 0
