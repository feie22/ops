jar_name="hadoop-yarn-server-resourcemanager-2.2.0.jar"
jar_dir="/software/servers/hadoop-2.2.0/share/hadoop/yarn"
jar_http_source="http://172.17.44.113/iso/mercury_jar/${jar}"
#rm
#salt -L '172.19.167.15' cmd.run "wget ${jar_http_source} -O /tmp/${jar_name}" 
#salt -L '172.19.167.15' cmd.run "mv /tmp/${jar_name} ${jar_dir}/${jar_name}" 
#salt -L '172.19.167.15' cmd.run "chown hadp:hadoop ${jar_dir}/${jar_name}" 

#除rm之外其他节点
function_all_ex_rm(){
for n in `cat G` 
do
    #salt -N "$n" cmd.run "wget ${jar_http_source} -O /tmp/${jar_name}" 
    #salt -N "$n" cmd.run "mv /tmp/${jar_name} ${jar_dir}/${jar_name}"  
    #salt -N "$n" cmd.run "chown hadp:hadoop ${jar_dir}/${jar_name}" 

    echo $n
done
}
function_all_ex_rm
