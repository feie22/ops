#!/usr/bin/env bash
cluster=$1
set -e
TODAY=`date +"%Y-%m-%d"`
TS=`date +"%Y-%m-%d %H:%M:%S"`
test_table="test_metastore_server_performance_$cluster_$USER"
echo "[$TS]******************Test[$cluster:$USER] Metastore Performance*************"
SQL="
drop table $test_table;
create table $test_table(id string)partitioned by (dt string);
alter table $test_table add partition (dt='$TODAY')"
waitfor=10
START=`date +"%Y-%m-%d %H:%M:%S"`
hive -e "$SQL">/dev/null 2>&1 &
commandpid=$!
( sleep $waitfor ; kill -9 $commandpid  > /dev/null 2>&1 ) &
watchdog=$!
sleeppid=$PPID
wait $commandpid > /dev/null 2>&1
END=`date +"%Y-%m-%d %H:%M:%S"`
DELAY=$(($(date +%s -d "$END") - $(date +%s -d "$START")))
echo "Send data to Hadooppecker,delay:$DELAY"
curl -d 'jsonData={"data":{"metastore_delay_$cluster_$USER":"'$DELAY'"},"monitorObject":"metastore_monitor"}&token=a71b4d92521ceec69ee6e4e1082bfdfcf60ac3b20f7e825908c5e6b380c30b8b' http://172.22.182.25:5988/HttpData
kill $sleeppid > /dev/null 2>&1
