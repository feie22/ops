#!/bin/bash
#ip_list=`cat append_ip| sed ':t;N;s/\n/,/;b t'` 
for cn in `cat a | awk '{print $2}'`
do
    echo $cn
    tags=`cat a | grep -w "$cn" | awk '{print $3","$1}'`
    echo $tags
    ip_list=`curl -s "http://bdp.jd.com/ops/api/server/searchIpsByTags.ajax?tags=$tags&appKey=123456&erp=zhangqiuying" |jq .data.dataList[].ip| tr -d "\""|sed ':t;N;s/\n/,/;b t'` 
    salt -L $ip_list cmd.run 'cat /etc/ganglia/gmond.conf | grep -C 10 udp_send_channel | grep "host=" ;cat /etc/ganglia/gmond.conf | grep -C 1 cluster| grep name'
done
#salt -L $ip_list cmd.run "/etc/init.d/gmond status"
#salt -L $ip_list saltutil.sync_all
#salt -L $ip_list saltutil.refresh_pillar 
#salt -L $ip_list pillar.get diana 
#salt -L $ip_list ganglia_util.sync_conf "{{ pillar.athene }}"

