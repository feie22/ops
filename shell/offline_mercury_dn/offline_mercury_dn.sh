#!/bin/sh
dir=`pwd`
cd $dir
TODAY=`date +%Y%m%d`
cluster_file="/etc/salt/master.d/cluster.conf"
cp $cluster_file ${cluster_file}.bak_$TODAY

echo "-----$TODAY offline iplist----" >>offline.log
for ip in `cat offline_ip`
do
    sed -i "/mercury_dn:/s/$ip,//g" $cluster_file
    sed -i "/mercury_dn:/s/,$ip,/,/g" $cluster_file
    sed -i "/mercury_dn:/s/,$ip'/'/g" $cluster_file
    echo "$TODAY $ip" >>offline.log
done
