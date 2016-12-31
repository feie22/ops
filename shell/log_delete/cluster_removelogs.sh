#!/bin/bash
#this script is used to remove logs on /data0,/data1
#writen by fanshiyi
#2016/04/13
#version 0.1

#### clear product cluster hadoop hadoop-logs & yarn-logs keep 7 days log
hadoop_log_dir=/data0/hadoop-logs
yarn_log_dir=/data1/yarn-logs
if [[ -d $hadoop_log_dir ]]
then
    find $hadoop_log_dir -type f -ctime +7 |xargs \rm -f
fi
if [[ -d $yarn_log_dir ]]
then
    find $yarn_log_dir -type f -ctime +7 |xargs \rm -f
fi

#### clear product cluster HBASE hbase-logs & logs; keep 7 days log
hbase_log_dir1=/data0/hbase-logs
hbase_log_dir2=/data0/logs/hbase-logs
if [[ -d $hbase_log_dir1 ]]
then
    find $hbase_log_dir1 -type f -ctime +7 |xargs \rm -f
fi
if [[ -d $hbase_log_dir2 ]]
then
    find $hbase_log_dir2 -type f -ctime +7 |xargs \rm -f
fi

#### clear product cluster JDQ kafka-logs; keep 30 days log
kafka_log_dir=/data0/kafka-logs
if [[ -d $kafka_log_dir ]] 
then
    find $kafka_log_dir -type f -ctime +30 |xargs \rm -f
fi

#### clear product cluster  JRC logs; keep 7 days log
jrc_log_dir=/data0/logs
if [[ -d $jrc_log_dir ]]
then
    find $jrc_log_dir -type f -name "*.log.*" -ctime +7 |xargs \rm -f
fi
#### clear product cluster  JES es-logs; keep 30 days log
jes_log_dir=/data0/es-logs
if [[ -d $jes_log_dir ]]
then
    find $jes_log_dir -type f -ctime +30 |xargs \rm -f
fi

#### clear product cluster MAGPIE es-logs; keep 30 days log
magpie_log_dir1=/data0/data/magpie/logs
magpie_log_dir2=/data0/servers
if [[ -d $magpie_log_dir1 ]] 
then
    find $magpie_log_dir1 -name "*.log.*" -type f -ctime +30 |xargs \rm -f
fi
if [[ -d $magpie_log_dir2 ]]
then
    for path in `find $magpie_log_dir2 -name "magpie_v*.*.*"  -type d`
    do
        if [[ -d $path ]]
        then
            find $path -name "*.log.*" -type f -ctime +30 |xargs \rm -f
        fi
    done
fi
