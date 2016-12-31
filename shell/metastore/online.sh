#!/bin/sh
for u in `cat /root/metastore/user.list`
do
    #salt -L '172.19.154.29' state.sls hadoop220.jdhive200.$u.$u test=true
    #salt -L '172.19.154.29' state.sls hadoop220.jdhive200.$u.$u
    #salt -L '172.19.154.30' state.sls hadoop220.jdhive200.$u.$u
    #echo "'"$u"'"
    #salt -L '172.19.154.29' cmd.run "su - $u -c 'jps | grep RunJar | xargs kill' "
    #salt -L '172.19.154.30' cmd.run "su - $u -c 'jps | grep RunJar | xargs kill' "
    #sleep 1
    #salt -L '172.19.154.29' cmd.run "su - $u -c 'nohup hive --service metastore > /data0/Logs/"$u"/"$u".hive-meta-store.log &' "
    #salt -L '172.19.154.30' cmd.run "su - $u -c 'nohup hive --service metastore > /data0/Logs/"$u"/"$u".hive-meta-store.log &' "
    #salt -L '172.19.154.29' cmd.run "su - $u -c 'jps' "
    salt -L '172.19.154.30' cmd.run "su - $u -c 'jps' "
    echo $u
done
