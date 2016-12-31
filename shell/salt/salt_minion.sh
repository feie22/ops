#!/bin/sh
##############################################
#Author zhangqiuying@jd.com
#Date  2016
#update 2016-05-03
Usage() {
    echo -e " -------------------------------------------------------------- " 
    echo -e "|Usage: bash salt_minion.sh {salt-master_id}                    |" 
    echo -e "|       1.salt-maste_id:20|84                                   |"
    echo -e " ---------------------------------------------------------------" 

}
server_release=`cat /etc/redhat-release |awk -F "release" '{print $2}'|awk  -F '' '{OFS="";print $2}'`
if [ `grep -w "IPADDR" -q /etc/sysconfig/network-scripts/ifcfg-eth0;echo $?` -eq 0 ]
then
    IP_tail=`grep IPA /etc/sysconfig/network-scripts/ifcfg-eth0 |awk -F. '{print $3$4}'`
    IP=`grep IPA /etc/sysconfig/network-scripts/ifcfg-eth0 |awk -F '=' '{print $2}'`
elif [ `grep -w "IPADDR" -q /etc/sysconfig/network-scripts/ifcfg-eth2;echo $?` -eq 0 ]
then
    IP_tail=`grep IPA /etc/sysconfig/network-scripts/ifcfg-eth2 |awk -F. '{print $3$4}'`
    IP=`grep IPA /etc/sysconfig/network-scripts/ifcfg-eth2 |awk -F '=' '{print $2}'`
else
    IP_tail=`grep IPA /etc/sysconfig/network-scripts/ifcfg-bond1 |awk -F. '{print $3$4}'`
    IP=`grep IPA /etc/sysconfig/network-scripts/ifcfg-bond1 |awk -F '=' '{print $2}'`
fi

#安装salt-minion
which salt-minion &> /dev/null
if [ $? -eq 0 ];then
    echo "salt-minion already installed!"
else
    if [ $server_release == 7 ];then
        wget http://172.22.99.122/iso/saltrpm_2016.3_centos7.tar.gz -O /tmp/saltrpm.tar.gz
    else
        wget http://172.22.99.122/iso/saltrpm_2016.3_centos6.tar.gz -O /tmp/saltrpm.tar.gz
    fi
    cd /tmp && tar -zxvf saltrpm.tar.gz && cd /tmp/salt/
    #rpm -Uvh *.rpm
    yum -y localinstall *.rpm
    cd /tmp
    rm -rf saltrpm.tar.gz salt
fi
chkconfig salt-minion on
#salt-minion配置
echo "master:
  - 172.19.185.84
  - 172.22.88.20
random_reauth_delay: 60
id: $IP
tcp_pub_port: 8010
tcp_pull_port: 8011
master_port: 8006">/etc/salt/minion
rm -f /etc/salt/pki/minion/minion_master.pub
service salt-minion restart
