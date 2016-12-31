#!/usr/bin/env bash
#
#
#################################################################
# 调整集群队列资源
################################################################
#
# 操作集群
des_cluster=wukong

# 获取配置文件的服务器和路径
remote_execution_ip=172.17.46.147 #client dd_edw
remote_execution_file_path=http://${remote_execution_ip}:8485/hadoop-conf/${des_cluster}
hadoop_conf_dir=/software/servers/hadoop-2.7.1/etc/nm_conf

# 备份文件路径
backup_path=backup

echo "`date` 开始执行..."

# 操作的配置文件
replace_conf_file=fair-scheduler.xml

cd $hadoop_conf_dir
echo "`date` 下载配置文件: $remote_execution_file_path/${replace_conf_file}"

# 下载新配置文件
wget -q $remote_execution_file_path/${replace_conf_file} -O ${replace_conf_file}.update

if [ ! -s ${replace_conf_file}.update ]; then
    echo "The file '$replace_conf_file' is not exist."
    echo "`date` execute exception"
    exit 1
else
    if [ ! -d $backup_path ]; then
        mkdir $backup_path
    fi

    mv $replace_conf_file ${backup_path}/${replace_conf_file}.bak."`date "+%Y%m%d%H%M%S"`"
    mv ${replace_conf_file}.update $replace_conf_file
    chown hadp.hadoop $replace_conf_file
    echo "`date` 操作完成"
fi
#开始刷新配置
echo \"`date` 开始刷新\"
ssh yarn@172.22.90.129 "yarn rmadmin -refreshQeues"
echo \"`date` 操作完成\"

/home/autodeploy/task/sendmail.py `echo $0|cut -c 3-` "执行完成"
