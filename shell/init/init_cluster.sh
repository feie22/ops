#!/bin/sh
##############################################
#Author zhangqiuying@jd.com
#Date  2016
#update 2016-03-25

#passwd config
#root ：集群
passwd_root_cluster="riy8Y_F8j5kFg_BB-2y_Wj=3T"
#root ：客户端
passwd_root_other="Q_nMHsUHPWA9cFxQt_sr"
#普通用户：hadp yarn mapred
passwd_m="Cwdmq_Zdxgsdz_Nsz1j_Hyxtdgj"
#普通用户：other
passwd_c="aaaaaa"
server_release=`cat /etc/redhat-release |awk -F "release" '{print $2}'|awk  -F '' '{OFS="";print $2}'`
Usage() {
    echo -e " ------------------------------------------------------------------    " 
    echo -e "|Usage: bash init_cluster {raid}  {product_line} {cluster_name}        |" 
    echo -e "|       1.raid: raid10|raid50|noraid                                   |"
    echo -e "|       2.product_line: client|hadoop|hbase|jdq|jes|jrc|magpie|mfs     |"
    echo -e "|       3.cluster_name: none|jdw|jmart|mercury|auge|and so on...       |"
    echo -e " -------------------------------------------------------------------    " 

}
function_raid10mkfs(){
#下载 create raid10 的脚本
wget http://172.22.99.122/iso/init/Toraid10mkfs.sh -O /tmp/Toraid10mkfs.sh
#create raid10 && mkfs
sh /tmp/Toraid10mkfs.sh
wait
#确定 raid10&&mkfs 完成
df -h| grep "data0" &> /dev/null
result=$?
s=1
while [ $result -ne 0 ]
do
    df -h| grep "data0" &> /dev/null
    result=$?
    sleep 2 
    if [ $s -ge 5 ]
    then
        echo "create raid10 timeout!"
        exit 1 

    fi
    s=`expr $s + 1`
    echo $s
done
}
function_raid50mkfs(){
#下载 create raid50 的脚本
wget http://172.22.99.122/iso/init/Toraid50mkfs.sh -O /tmp/Toraid50mkfs.sh
##create raid50 && mkfs
sh /tmp/Toraid50mkfs.sh
wait
#确定 raid50&&mkfs 完成
df -h| grep "data0" &> /dev/null
result=$?
s=1
while [ $result -ne 0 ]
do
    df -h| grep "data0" &> /dev/null
    result=$?
    sleep 2
    if [ $s -ge 5 ]
    then
        echo "create raid50 timeout!"
        exit 1

    fi
    s=`expr $s + 1`
    echo $s
done
}
function_auth_keys(){
mkdir /root/.ssh
touch /root/.ssh/authorized_keys
echo "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAwvJlQIsnhpi8F0YGbvSxVNz/g2kHOQTdAUNMkjaEfrPDo5Jzthpmf0+cS8pXqiemwEXgigmaH3gS4+41lXNqNNWSzNtIWLRJseSDNm0X1w1S8pIybJz/llSgZHVY+t4RCs1nY629hY5jldPxAXdprK+1FqoixABJFib2FLdLhbvhdxJvqWLIUv0kpTkHmZ6gtJHBF/TTVMidWBWvHRaPzJa7eAt0Lpps3R2pu8CoXyntZjwX36HdY1PNR+u3/KCXUOXFr0KkxCDzEDxoPgR5C2x21HTa1vYTQxL4urNMmf22xErbKzE6ccQ9/ZkL39jfVcrPpMd9RS71Ppd5AIf4ww== root@BJ-YZH-1-H1-44209.360buy.com" >/root/.ssh/authorized_keys
chmod 640 /root/.ssh/authorized_keys
chmod 700 /root/.ssh
}
function_hostname(){
if [ `grep -w "IPADDR" -q /etc/sysconfig/network-scripts/ifcfg-eth0;echo $?` -eq 0 ]
then
    IP_tail=`grep IPA /etc/sysconfig/network-scripts/ifcfg-eth0 |grep -v ^# |awk -F. '{print $3$4}'`
    IP=`grep IPA /etc/sysconfig/network-scripts/ifcfg-eth0 |grep -v ^#|awk -F '=' '{print $2}'`
elif [ `grep -w "IPADDR" -q /etc/sysconfig/network-scripts/ifcfg-eth2;echo $?` -eq 0 ]
then
    IP_tail=`grep IPA /etc/sysconfig/network-scripts/ifcfg-eth2|grep -v ^# |awk -F. '{print $3$4}'`
    IP=`grep IPA /etc/sysconfig/network-scripts/ifcfg-eth2 |grep -v ^#|awk -F '=' '{print $2}'`
elif [ `grep -w "IPADDR" -q /etc/sysconfig/network-scripts/ifcfg-bond1;echo $?` -eq 0 ]
then
    IP_tail=`grep IPA /etc/sysconfig/network-scripts/ifcfg-bond1|grep -v ^# |awk -F. '{print $3$4}'`
    IP=`grep IPA /etc/sysconfig/network-scripts/ifcfg-bond1 |grep -v ^#|awk -F '=' '{print $2}'`
else
    IP_tail=`ip -o -4 addr show | awk -F '[ /]+' '/global/ {print $4}'|awk -F. '{print $3$4}'`
    IP=`ip -o -4 addr show | awk -F '[ /]+' '/global/ {print $4}' `
fi
#echo $IP_tail,$IP
case "$IP" in
    172.17.*.*)
        M="BJYZ"
        ;;
    172.22.*.*)
        M="BJHC"
        ;;
    172.16.*.*|172.19.*.*)
        M="BJYF"
        ;;
    172.20.*.*)
        M="LF"
        ;;
    172.18.*.*)
        M="M6"
        ;;
    172.28.*.*)
        M="MJQ"
        ;;
    *)
        M="UNKNOWN"
        ;;
esac
PL=`echo $1|tr '[a-z]' '[A-Z]'`
CN=`echo $2|tr '[a-z]' '[A-Z]'`
if [ $CN == "NONE" ];then
	Name="${M}-${PL}"
else
	Name="${M}-${PL}-$CN"
fi
Nametail="hadoop.jd.local"
HOSTNAME="$Name-${IP_tail}.$Nametail"
#echo $HOSTNAME
if [ $server_release == 7 ];then
    echo "$Name-${IP_tail}.$Nametail" >/etc/hostname
else
    echo "NETWORKING=yes
NETWORKING_IPV6=no
HOSTNAME=$Name-${IP_tail}.$Nametail" >/etc/sysconfig/network
fi
echo $Name-${IP_tail}.$Nametail
hostname $Name-${IP_tail}.$Nametail
}
#function_hostname $2 $3
function_user(){
#各产品线服务器root密码初始化
PL=$1
case "$PL" in
    "client")
        #echo "客户端root密码"
        echo "${passwd_root_other}"|passwd --stdin root
        ;;
    *)
        #echo "集群root密码"
        echo "$passwd_root_cluster"|passwd --stdin root
        ;;
esac
#各产品线普通用户账号密码初始化
user_hadp="hadp"
user_yarn="yarn"
user_jdq="jdq"
user_jes="jes"
user_jrc="jrc"
user_magpie="magpie"

case "$PL" in
    "hadoop")
        grep "^${user_hadp}" /etc/passwd &> /dev/null
        if [ ! "$?" -eq 0 ]
        then
            #echo "添加用户${user_hadp}"
            useradd ${user_hadp}
            echo "${passwd_m}"|passwd --stdin ${user_hadp}
        fi
        grep "^${user_yarn}" /etc/passwd &> /dev/null
        if [ ! "$?" -eq 0 ]
        then
            #echo "添加用户${user_yarn}"
            useradd ${user_yarn}
            echo "${passwd_m}"|passwd --stdin ${user_yarn}
        fi
        ;;
    "jdq")
        grep "^${user_jdq}" /etc/passwd &> /dev/null
        if [ ! "$?" -eq 0 ]
        then
            #echo "添加用户${user_jdq}"
            useradd ${user_jdq}
            echo "${passwd_c}"|passwd --stdin ${user_jdq}
        fi
        #删除除了jdq之外的其他用户
        user=`ls -l /home/ | awk '{print $9}'|grep -v 'jdq'`
        for u in $user
        do
            #echo "删除用户$u"
            userdel -r $u
        done
        ;;
    "jes")
        grep "^${user_jes}" /etc/passwd &> /dev/null
        if [ ! "$?" -eq 0 ]
        then
            #echo "添加用户${user_jes}"
            useradd ${user_jes}
            echo "${passwd_c}"|passwd --stdin ${user_jes}
        fi
        #删除除了jes之外的其他用户
        user=`ls -l /home/ | awk '{print $9}'|grep -v 'jes'`
        for u in $user
        do
            #echo "删除用户$u"
            userdel -r $u
        done
        ;;
    "jrc")
        grep "^${user_jrc}" /etc/passwd &> /dev/null
        if [ ! "$?" -eq 0 ]
        then
            #echo "添加用户${user_jrc}"
            useradd ${user_jrc}
            echo "${passwd_c}"|passwd --stdin ${user_jrc}
        fi
        #删除除了jrc之外的其他用户
        user=`ls -l /home/ | awk '{print $9}'|grep -v 'jrc'`
        for u in $user
        do
            #echo "删除用户$u"
            userdel -r $u
        done
        ;;
    "magpie")
        grep "^${user_magpie}" /etc/passwd &> /dev/null
        if [ ! "$?" -eq 0 ]
        then
            #echo "添加用户${user_magpie}"
            useradd ${user_magpie}
            echo "${passwd_c}"|passwd --stdin ${user_magpie}
        fi
        ;;
    *)
        grep "^${user_hadp}" /etc/passwd &> /dev/null
        if [ ! "$?" -eq 0 ]
        then
            #echo "添加用户${user_hadp}"
            useradd ${user_hadp}
            echo "${passwd_m}"|passwd --stdin ${user_hadp}
        fi
        echo "${passwd_m}"|passwd --stdin ${user_hadp}
        ;;
esac
}
#function_user $2
function_iftop(){
which iftop &> /dev/null
if [ $? -eq 0 ];then
    echo "iftop already installed!"
else
    cd /tmp/
    wget http://172.22.99.122/iso/iftop-1.0-0.7.pre4.el6.x86_64.rpm
    rpm -ivh iftop-1.0-0.7.pre4.el6.x86_64.rpm
    wait
    rm -f /tmp/iftop-1.0-0.7.pre4.el6.x86_64.rpm
fi
}
function_daemontools(){
cd /software/servers/
wget http://172.22.96.55/packages/daemontools-0.76.tar.gz
tar zxvf daemontools-0.76.tar.gz
/bin/rm -rf daemontools-0.76.tar.gz
cd daemontools-0.76
./package/install
#chown -R jrc:jrc /software/servers/daemontools-0.76
}
#赋权
function_auth(){
PL=$1
case "$PL" in
    "jdq")
        echo "software&data赋权给jdq"
        function_iftop
        #给普通用户赋权iftop
        chmod 4755 `which iftop`
        chown -R jdq:jdq /software/servers
        chown -R jdq:jdq /data*
        ;;
    "jes")
        echo "software&data赋权给jes"
        chown -R jes:jes /software/servers
        chown -R jes:jes /data*
        ;;
    "magpie")
        echo "software&data赋权给magpie"
        chown -R magpie:magpie /software/servers
        chown -R magpie:magpie /data*
        ;;
    "jrc")
        echo "software&data赋权给jrc"
        function_iftop
        function_daemontools
        #给普通用户赋权iftop
        chmod 4755 `which iftop`
        chown -R jrc:jrc /software/servers
        chown -R jrc:jrc /data*
        ;;
    *)
        echo "非jdq&jes&magpie&jrc无需特殊赋权操作"
        ;;
esac
}
#修改系统参数配置
function_sys_conf(){
PL=$1
case "$PL" in
    "jes")
        echo "修改jes的系统参数"
        #sysctl配置修改并生效
        echo "vm.max_map_count = 262144" >>/etc/sysctl.conf
        sed -i 's/vm.swappiness = 0/vm.swappiness = 1/g' /etc/sysctl.conf
        sysctl -w vm.max_map_count=262144
        sysctl vm.swappiness=1
        #limits配置修改并生效
        echo "* soft memlock 40000000" >>/etc/security/limits.conf
        echo "* hard memlock 40000000" >>/etc/security/limits.conf
        ulimit -l 40000000
        ;;
    "magpie")
        #修改magpie的cgroup配置
        echo "group magpie{
    perm{
        task{
            uid = magpie;
            gid = magpie;
        }
        admin{
            uid = magpie;
            gid = magpie;
        }
    }
    cpu {}
    memory {}
}">>/etc/cgconfig.conf 
        service cgconfig restart
        ;;
    "jrc")
        echo "修改系统hosts"
        sed -i "/${IP_tail}.hadoop.jd.local/d" /etc/hosts
        echo "$IP $Name-${IP_tail}.$Nametail">>/etc/hosts
        echo "修改jrc的系统参数"
        sed -ri 's/(net.ipv4.ip_local_port_range = )(1024  65535)/\110000 65535/' /etc/sysctl.conf
        /sbin/sysctl -p
        #修改jrc的cgroup配置
        echo "group storm {
    perm {
        task {
            uid = jrc;
            gid = jrc;
        }
        admin {
            uid = jrc;
            gid = jrc;
        }
    }
    cpu {
    }
    memory { 
    }
}">>/etc/cgconfig.conf
        service cgconfig restart
        ;;
    *)
        echo "非jes&magpie&jrc无需修改系统参数"
        ;;
esac
}
#function_auth $2 
function_salt_minion(){
#安装salt-minion
yum -y remove salt zero*
if [ $server_release == 7 ];then
    wget http://172.22.99.122/iso/saltrpm_centos7.tar.gz -O /tmp/saltrpm.tar.gz
else
    wget http://172.22.99.122/iso/saltrpm_centos6.tar.gz -O /tmp/saltrpm.tar.gz
fi
cd /tmp && tar -zxvf saltrpm.tar.gz && cd /tmp/salt/
#rpm -Uvh *.rpm
yum -y localinstall *.rpm
cd /tmp
rm -rf saltrpm.tar.gz salt

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
}
#function_salt_minion $3
function_ganglia(){
#install ganglia gmond
which gmond &> /dev/null
if [ $? -eq 0 ];then
    echo "gmond already installed!"
else
    if [ $server_release == 7 ];then
        wget http://172.22.99.122/iso/gangliarpm_centos7.tar.gz -O /tmp/gangliarpm.tar.gz
    else
        wget http://172.22.99.122/iso/gangliarpm_centos6.tar.gz -O /tmp/gangliarpm.tar.gz
    fi
    cd /tmp && tar -zxvf gangliarpm.tar.gz && cd /tmp/ganglia/
    # rpm -Uvh *.rpm
    yum -y localinstall *.rpm
    cd /tmp
    rm -rf gangliarpm.tar.gz ganglia
fi
chkconfig gmond on
}
#function_ganglia

function_download(){
case "$1" in
    "hbase")
        cd /software/servers/softwarebak
        wget http://172.22.99.122/iso/hadoop-2.2.0.tar.gz -O hadoop-2.2.0.tar.gz
        wget http://172.22.99.122/iso/hadoop-2.6.1.tar.gz -O hadoop-2.6.1.tar.gz
        wget http://172.22.99.122/iso/hbase-0.94.18-security.tar.gz -O hbase-0.94.18-security.tar.gz
        wget http://172.22.99.122/iso/hbase-1.1.2.tar.gz -O hbase-1.1.2.tar.gz
        wget http://172.22.99.122/iso/zookeeper-3.4.5.tar.gz -O zookeeper-3.4.5.tar.gz
        ;;
    *)
        echo "无需下载"
        ;;
esac
}

argv=$#
if [ $passwd_root_cluster == "aaaaaa" ];then
	echo "At first please chang the script var \$passwd !!!"
	Usage
	exit 1
elif [[ $argv -eq 3 ]];then
    RAID=$1
    case "$RAID" in
        "raid10")
            function_raid10mkfs
            #echo "raid10mkfs"
            ;;
        "raid50")
            function_raid50mkfs
            #echo "raid50mkfs"
            ;;
        "noraid")
            echo "noraid!"
            ;;
        *)
            echo "please choice the right raid option!" 
            Usage
            exit 1
    esac
    function_auth_keys
    function_hostname $2 $3
    function_user $2
    function_auth $2
    function_sys_conf $2
    function_salt_minion
    function_ganglia
    function_download $2
else
    Usage
    exit 1
fi
