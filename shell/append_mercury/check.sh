#!/bin/bash
f='/software/servers/hadoop-2.2.0/etc/hadoop/hdfs-site.xml'
#salt -N 'mercury_dn' cmd.run "md5sum $f"
#salt -N 'mercury_ns1_nn' cmd.run "md5sum $f"  
#salt -N 'mercury_ns2_nn' cmd.run "md5sum $f"
#salt -N 'mercury_ns3_nn' cmd.run "md5sum $f"
#salt -N 'mercury_ns1_jh' cmd.run "md5sum $f"
#salt -N 'mercury_ns2_jh' cmd.run "md5sum $f"
#salt -N 'mercury_ns3_jh' cmd.run "md5sum $f"
#salt -L '172.19.167.15' cmd.run "md5sum $f"
salt -L `cat nn.list | sed ':t;N;s/\n/,/;b t'` cmd.run 'su - hadp -c "jps"'
