#!/bin/bash
salt -N 'mercury_dn' cmd.run "su - yarn -c '/bin/rm -rf /data*/yarn1/local/*'"
salt -N 'mercury_dn' cmd.run "su - yarn -c '/bin/rm -rf /data*/yarn1/logs/*'"
#salt -L '172.19.153.49' cmd.run "su - yarn -c '/bin/rm -rf /data0/yarn1/local/*'" 
