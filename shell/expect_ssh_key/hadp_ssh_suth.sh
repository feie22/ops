#!/bin/bash

#passwd='1qaz@WSX'
passwd='Cwdmq_Zdxgsdz_Nsz1j_Hyxtdgj'

cat $HBASE_HOME/conf/regionservers | while read line 
do
host=$line
expect << EOF
spawn ssh-copy-id -i /home/hadp/.ssh/id_rsa.pub $host
expect {
    "yes/no" {   
        send "yes\r";exp_continue 
    }
    "*password:" {   
        send "$passwd\r";exp_continue 
    }
    "*密码:" {   
        send "$passwd\r";exp_continue 
    }

}
EOF
sleep 1
done
