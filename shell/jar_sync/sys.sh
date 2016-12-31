#!/bin/sh
#salt -L '172.19.167.15' cmd.run 'echo never > /sys/kernel/mm/redhat_transparent_hugepage/defrag'
#salt -L '172.19.167.15' cmd.run 'echo never > /sys/kernel/mm/redhat_transparent_hugepage/enabled'
function_all_ex_rm(){
for n in `cat G`
do
    salt -N "$n" cmd.run "echo never > /sys/kernel/mm/redhat_transparent_hugepage/defrag" 
    salt -N "$n" cmd.run "echo never > /sys/kernel/mm/redhat_transparent_hugepage/enabled" 

    echo $n
done
}
function_all_ex_rm
