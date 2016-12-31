export iplist="172.22.214.48,172.22.214.49,172.22.214.52,172.22.214.51,172.22.214.88,172.22.214.89,172.22.214.97,172.22.213.85,172.22.213.82,172.22.213.72,172.22.213.73,172.22.213.54,172.22.213.69,172.22.213.70,172.22.214.100,172.22.214.109,172.22.214.112,172.22.212.73,172.22.212.94,172.22.212.91,172.22.212.55"
salt -L $iplist buffalo_util.stop bdp_client
salt -L $iplist os_util.useradd bdp_client 3456
salt -L $iplist os_util.mkdir '/data0 /data0/logs /data0/tmp_data /data0/tmp /data0/tmp_data/bidata /data0/tmp_data/bi_data_load /data0/tmp_data/plumber_data /data0/tmp_data/log_data /data0/tmp_data/SourceTable /data0/logs/hadoop-2.2.0 /data0/logs/hive-0.12.0 /data0/logs/hive-0.14.0 /data0/logs/plumber2.0 /data0/logs/plumber /data0/logs/plumberwms /data0/logs/apache-tomcat-6.0.20_2 /data0/logs/push_hbase /data0/logs/schedule /data0/logs/schedule/tasknode /data0/logs/schedule/tasknode/task /data0/tmp_data/buffalo_script /data0/logs/martSync' bdp_client bdp_client 755
salt -L $iplist os_util.mkdir '/data0/tmp' root root 777
salt -L $iplist setup_util.setup public jdk version=1.6.0_25 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup public jdk version=1.7.0_45 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup public jdk version=1.7.0_67 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
##salt -L $iplist setup_util.setup bdp_client2.0_huidu pig version=0.13.0 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup bdp_client2.0_huidu plumber version=2.0 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup bdp_client2.0_huidu plumbersh user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup bdp_client2.0_huidu plumberwms user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup bdp_client2.0_huidu R version=3.2.1 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup bdp_client2.0_huidu schedule user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup bdp_client2.0_huidu udf user=bdp_client user_group=bdp_client auth=755 install_path=/software/
salt -L $iplist setup_util.setup bdp_client2.0_huidu apache-tomcat version=6.0.20_2 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup bdp_client2.0_huidu codelib user=bdp_client user_group=bdp_client auth=755 install_path=/data0/
salt -L $iplist setup_util.setup bdp_client2.0_huidu conf user=bdp_client user_group=bdp_client auth=750 install_path=/software/
salt -L $iplist setup_util.setup bdp_client2.0_huidu edw user=bdp_client user_group=bdp_client auth=755 install_path=/software/
salt -L $iplist setup_util.setup hadoop hadoop version=2.2.0 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup hadoop hadoop version=2.7.1 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup bdp_client2.0_huidu spark-1.5.2-HADOOP version=2.2.0 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup bdp_client2.0_huidu spark-1.5.2-HADOOP version=2.7.1 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup spark spark-1.6.1-HADOOP version=2.7.1 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup bdp_client2.0_huidu jdhive-2.0.0-HADOOP version=2.2.0 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup bdp_client2.0_huidu jdhive-2.0.0-HADOOP version=2.7.1 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup public oozie-4.2.0-HADOOP version=2.7.1 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup public oozie-4.1.0-HADOOP version=2.2.0 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup public tez-0.7.0-HADOOP version=2.7.1 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup public tez-0.7.0-HADOOP version=2.2.0 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup public lzo  user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup public bdp_tools  user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup public Python  version=3.2.3 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup public Python2.6 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist setup_util.setup public pig  version=0.15.0 user=bdp_client user_group=bdp_client auth=755 install_path=/software/servers
salt -L $iplist os_util.lns /software/udf /home/bdp_client/udf
salt -L $iplist os_util.lns /software/servers/schedule/tasknode/task/ /home/bdp_client/task
salt -L $iplist os_util.lns /data0/logs/schedule/tasknode/task /software/servers/schedule/tasknode/logs/task
salt -L $iplist os_util.lns /software/servers/Python2.6/bin/python2.6 /usr/bin/python2.6
salt -L $iplist os_util.mkdir /software/servers/schedule/tasknode/plugin/exec/exec_result bdp_client bdp_client 755
salt -L $iplist software_util.getfile ' {"cluster_name": "base", "filelist": [ {"update_time": "20151216", "salt_path": "/bdp_client2.0_huidu/bdp_client2.0/base/home/bdp_client/.bashrc", "auth": "700", "target_path": "/home/bdp_client/.bashrc", "user": "bdp_client", "user_group": "bdp_client", "md5": "12", "id": 293, "service_info_id": 22}], "install_path": "/software/", "service": "bdp_client", "result": "true"}' 
salt -L $iplist os_util.lns /bin/bash /bin/sh_bak
#salt -L $iplist os_util.rm /bin/sh
salt -L $iplist software_util.getfile ' {"cluster_name": "base", "filelist": [{"update_time": "20151202", "salt_path": "/bdp_client2.0_huidu/bdp_client2.0/base/bin/sh", "auth": "755", "target_path": "/bin/sh", "user": "root", "user_group": "root", "md5": "", "id": 200, "service_info_id": 22}, {"update_time": "20151216", "salt_path": "/bdp_client/bdp_client/base/home/bdp_client/.bashrc", "auth": "700", "target_path": "/home/bdp_client/.bashrc", "user": "bdp_client", "user_group": "bdp_client", "md5": "12", "id": 293, "service_info_id": 22}], "install_path": "/software/", "service": "bdp_client", "result": "true"}' 
salt -L $iplist buffalo_util.setBinSh
salt -L $iplist buffalo_util.initClient
salt -L $iplist buffalo_util.setNodeId
salt -L $iplist os_util.yum 'mysql lftp perl-ExtUtils-CBuilder perl-ExtUtils-MakeMaker '
salt -L $iplist buffalo_util.start bdp_client
#salt -L $iplist label_util.changelabel add '[ { "key": "在线状态", "subKey": [ "上线" ] } ]' '{{ grains.id }}' template='jinja'
#salt -L $iplist label_util.changelabel add '[ { "key": "客户端", "subKey": [ "标准客户端2.0" ] } ]' '{{ grains.id }}' template='jinja'
#salt -L $iplist label_util.changelabel add '[ { "key": "集群名称", "subKey": [ "客户端2.0" ] } ]' '{{ grains.id }}' template='jinja'
#salt -L $iplist label_util.changelabel del '[ { "key": "在线状态", "subKey": [ "待上线" ] } ]' '{{ grains.id }}' template='jinja'
