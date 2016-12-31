#!/bin/sh
for d in `cat /root/metastore/user.list`
do
    #chown -R salt.salt /srv/salt/hadoop220/jdhive200/$d
    #mv /srv/salt/hadoop220/jdhive200/$d/mart_mobile.sls /srv/salt/hadoop220/jdhive200/$d/$d.sls
    #mv /srv/salt/hadoop220/jdhive200/$d/conf_mart_mobile /srv/salt/hadoop220/jdhive200/$d/conf_$d
    #sed -i "s/mart_mobile/$d/g" /srv/salt/hadoop220/jdhive200/$d/$d.sls
    #sed -i "s/mart_mobile/$d/g" /srv/salt/hadoop220/jdhive200/$d/conf_$d/*
done
