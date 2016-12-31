#append_ip=`cat append_ip|sed -e   ':a;N;s/\n/,/;ta'`
#echo "'$append_ip'"

#salt -L $append_ip  test.ping
#salt -L $append_ip state.sls mercury.sls.append
salt -N 'mercury_ns1_nn' state.sls mercury.sls.ns1
salt -N 'mercury_ns2_nn' state.sls mercury.sls.ns2
salt -N 'mercury_ns3_nn' state.sls mercury.sls.ns3
#salt -N 'mercury_ns1_jh' state.sls mercury.sls.ns1_jh
#salt -N 'mercury_ns2_jh' state.sls mercury.sls.ns2_jh
#salt -N 'mercury_ns3_jh' state.sls mercury.sls.ns3_jh
salt -L '172.19.167.15' state.sls mercury.sls.rm
salt -N 'mercury_dn' state.sls mercury.sls.dn
#hosts
#salt -N 'mercury_ns1_nn' state.sls mercury.sls.hosts
#salt -N 'mercury_ns2_nn' state.sls mercury.sls.hosts
#salt -N 'mercury_ns3_nn' state.sls mercury.sls.hosts
#salt -L '172.19.167.15' state.sls mercury.sls.hosts 
#salt -N 'mercury_dn' state.sls mercury.sls.hosts
#刷新
#salt -N 'mercury_ns1_nn' cluster.refreshdfsnode
#salt -N 'mercury_ns2_nn' cluster.refreshdfsnode 
#salt -N 'mercury_ns3_nn' cluster.refreshdfsnode 
#salt -L '172.19.167.15' cluster.refreshyarnnode
#同步
#salt -L $append_ip saltutil.sync_all
#salt -L $append_ip  cluster.startdn
