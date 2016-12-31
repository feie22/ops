#!/bin/bash
salt -L `cat nn_d.list | sed ':t;N;s/\n/,/;b t'` cmd.run 'su - hadp -c "hadoop-daemon.sh start zkfc"'
