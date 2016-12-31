#!/bin/bash
#check network,dns,Raidlevel,disks after system installed
#author by fanshiyi March 18 2016

#path to run this script
path=`pwd`
#the ip list to check
file=ping.lst
#os root passwd


for ip in `cat ping.lst`
do
ssh -T $ip "exit" &> /dev/null
#network fping
stat=`fping $ip|awk '{print $3}'`
if [[ x"$stat" == xalive ]]
then
    echo ---------------------------------------------------
    echo $ip is alive
#check dns
fuction_dns()
    {
    stat1=`ssh $ip "grep 172.16.16.16 /etc/resolv.conf|wc -l"` 
    if [[ $stat1 -eq 0 ]]
        then
        echo "no dns found"
    else
        echo "dns is ok"
    fi
    }
fuction_dns
#MegaCli check raid level & echo the mount of disks
function_dspraid(){
    isMegaCli64=`ssh $ip "rpm -qa|grep MegaCli |wc -l"`
    if [[ $isMegaCli64 -lt 1 ]]
    then 
        ssh $ip "
        wget http://172.17.44.113/iso/MegaCli-8.07.14-1.noarch.rpm
        rpm -ivh MegaCli-8.07.14-1.noarch.rpm
        /bin/rm MegaCli-8.07.14-1.noarch.rpm
        " &> /dev/null
        raidlevel=`ssh $ip '/opt/MegaRAID/MegaCli/MegaCli64 -LDInfo -LALL -aALL|grep "RAID Level Qualifier-0"|cut -d":" -d"," -f1-2'`
        echo $raidlevel
        disk=`ssh $ip "ls /dev/sd[a-z]|wc -l|grep -v sda"`
        echo amount of disks:$disk
    else
        raidlevel=`ssh $ip '/opt/MegaRAID/MegaCli/MegaCli64 -LDInfo -LALL -aALL|grep "RAID Level Qualifier-0"|cut -d":" -d"," -f1-2'`
        echo $raidlevel
        disk=`ssh $ip "ls /dev/sd[a-z]|wc -l|grep -v sda"`
        echo amount of disks:$disk
    fi
    }
function_dspraid
else
echo $ip ping failed!
fi 
echo ---------------------------------------------------
done