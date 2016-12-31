#!/usr/bin/env bash
cd /software/servers/
wget http://172.22.96.55/packages/daemontools-0.76.tar.gz
tar zxvf daemontools-0.76.tar.gz
/bin/rm -rf daemontools-0.76.tar.gz
cd daemontools-0.76
./package/install
chown -R jrc:jrc /software/servers/daemontools-0.76
