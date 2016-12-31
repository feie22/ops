#!/bin/bash
#
netstat -anpt | awk '{print $5}'|sort |uniq -c | sort -nr | head -10

netstat -anpt | awk '{ips[$5]++} END{for(i in ips){if(ips[i]>200){print ips[i], i}} }' |sort -nr