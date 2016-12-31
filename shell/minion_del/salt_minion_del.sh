#!/bin/sh
#for ip in `cat minion_del.txt`
#do
#salt-key -d $ip -y
#sleep 1
#done
###
#direct rm file
###
m_path=/etc/salt/pki/master/minions
for ip in `cat  minion_del.txt`
do
  \rm $m_path/$ip
done

