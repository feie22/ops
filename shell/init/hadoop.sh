#!/bin/bash
# 下次启动不执行
sed -i '/hadoop/d' /etc/rc.d/rc.local

# 配置sysctl
cat >> /etc/sysctl.conf <<EOF
net.core.somaxconn = 32768
net.core.wmem_default = 8388608
net.core.rmem_default = 8388608
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_timestamps = 0
net.ipv4.tcp_synack_retries = 1
net.ipv4.tcp_syn_retries = 0
net.ipv4.tcp_tw_recycle = 1
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_mem = 94500000 915000000 927000000
net.ipv4.tcp_max_orphans = 3276800
net.ipv4.ip_local_port_range = 1024  65535
net.ipv4.tcp_fin_timeout = 10
net.ipv4.tcp_keepalive_time = 100
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.tcp_max_tw_buckets = 20000
vm.swappiness = 0
EOF

# 配置vim
server_release=`cat /etc/redhat-release |awk -F "release" '{print $2}'|awk  -F '' '{OFS="";print $2}'`
if [ $server_release == 7 ];then
    wget http://172.22.99.122/iso/molokai.vim -O /usr/share/vim/vim74/colors/molokai.vim    
else
    wget http://172.22.99.122/iso/molokai.vim -O /usr/share/vim/vim72/colors/molokai.vim
fi
cat >> /etc/vimrc <<EOF
filetype plugin indent on
set pastetoggle=<F9>
set paste
set autoindent
set smartindent
set cindent
set nobackup
set fdm=marker
set expandtab
set tabstop=4
set softtabstop=4
set shiftwidth=4
set incsearch
set laststatus=2
set statusline=%t%r%h%w\ [%Y]\ [%{&ff}]\ [%{&fenc}:%{&enc}]\ [%08.8L]\ [%p%%-%P]\ [%05.5b]\ [%04.4B]\ [%08.8l]%<\ [%04.4c-%04.4v%04.4V]
set encoding=utf-8
set fileencodings=ucs-bom,utf-8,cp936,gb18030,big5,latin1
set fileencoding=chinese
set guifont=宋体:h10
set t_Co=256
color molokai
EOF
#echo "alias vi='vim'" >> /etc/bashrc
#配置gateone lrz lsz
if [ $server_release == 7 ];then
    wget http://172.22.99.122/iso/rzsz/rzsz_centos7.pyc -O /etc/rzsz.pyc
    cat >> /etc/bashrc <<EOF
alias vi='vim'
alias lrz='python2.7 /etc/rzsz.pyc -d'
alias lsz='python2.7 /etc/rzsz.pyc -u'
export JAVA_HOME=/software/servers/jdk1.6.0_25
export PATH=\$JAVA_HOME/bin:\$PATH
EOF
else
    wget http://172.22.99.122/iso/rzsz/rzsz_centos6.pyc -O /etc/rzsz.pyc
    cat >> /etc/bashrc <<EOF
alias vi='vim'
alias lrz='python2.6 /etc/rzsz.pyc -d'
alias lsz='python2.6 /etc/rzsz.pyc -u'
export JAVA_HOME=/software/servers/jdk1.6.0_25
export PATH=\$JAVA_HOME/bin:\$PATH
EOF
fi
chmod 777 /etc/rzsz.pyc
# 禁用不用的服务
disable_useless_garbage(){
for i in `ls /etc/rc.d/init.d/*`; do
CURSRV=`echo $i|cut -c 18-`
echo $CURSRV
case $CURSRV in
crond | network | sshd | syslog | xinetd |sysstat | snmpd |rsyslog |nscd|cgconfig|cgred )
echo "Base services, Skip!"
;;
*)
echo "change $CURSRV to off"
chkconfig --level 235 $CURSRV off
service $CURSRV stop
;;
esac
done
service nscd start
chkconfig nscd on
}
disable_useless_garbage_centos7(){
for i in `ls /etc/systemd/system/multi-user.target.wants/*`; do
CURSRV=`echo $i|cut -c 45-`
echo $CURSRV
case $CURSRV in
crond.service|network.service|sshd.service|syslog.service|xinetd.service|sysstat.service|snmpd.service|rsyslog.service|nscd.service|cgconfig.service|cgred.service|salt-minion.service|gmond.service)
    echo "Base services, Skip!"
    ;;
*)
    echo "change $CURSRV to disable"
    systemctl disable $CURSRV
    systemctl stop $CURSRV
    ;;
esac
done
disable_useless_garbage
}
if [ $server_release == 7 ];then
    disable_useless_garbage_centos7
else
    disable_useless_garbage
fi

# 系统设置
set_system_config(){
## ssh设置
_sshd_file=/etc/ssh/sshd_config
sed -i "s/GSSAPIAuthentication yes/GSSAPIAuthentication no/g" $_sshd_file
sed -i "s/#UseDNS yes/UseDNS no/g" $_sshd_file
### 配置安全ssh
sed -i "s/#PermitEmptyPasswords no/PermitEmptyPasswords no/g" /etc/ssh/sshd_config

## 配置i18n
if [ $server_release == 7 ];then
    _lang_file="/etc/locale.conf"
else
    _lang_file="/etc/sysconfig/i18n"
fi
echo 'LANG="zh_CN.UTF-8"
SYSFONT="latarcyrheb-sun16"' > $_lang_file

## 关闭内存整理
if [ $server_release == 7 ];then
    _defrag_file="/sys/kernel/mm/transparent_hugepage/defrag"
    _enabled_file="/sys/kernel/mm/transparent_hugepage/enabled"
else
    _defrag_file="/sys/kernel/mm/redhat_transparent_hugepage/defrag"
    _enabled_file="/sys/kernel/mm/redhat_transparent_hugepage/enabled"
fi
echo never > $_defrag_file
echo never > $_enabled_file 
echo "echo never > $_defrag_file" >> /etc/rc.d/rc.local
echo "echo never > $_enabled_file" >> /etc/rc.d/rc.local

## 配置limits
_limits_file="/etc/security/limits.conf"
if [ $server_release == 7 ];then
    _nproc_file="/etc/security/limits.d/20-nproc.conf"
    _nofile_file="/etc/security/limits.d/20-nofile.conf"
    _stack_file="/etc/security/limits.d/20-stack.conf"
else

    _nproc_file="/etc/security/limits.d/90-nproc.conf"
    _nofile_file="/etc/security/limits.d/90-nofile.conf"
    _stack_file="/etc/security/limits.d/90-stack.conf"
fi
echo "*       -       nofile  65535" >>$_limits_file
sed -i "/^*/s/^/#/" $_nproc_file 
touch $_nofile_file 
touch $_stack_file
cat > $_nofile_file <<EOF
* soft nofile 65535
* hard nofile 65535
EOF
cat > $_nproc_file <<EOF
* soft nproc 65535
* hard nproc 65535
EOF
cat > $_stack_file <<EOF
* soft stack 65535
* hard stack 65535
EOF
}
set_system_config

# 配置grub
if [ $server_release == 7 ];then
    echo "CENTOS7.1 NO GRUB CONFIG"
else
    touch /root/grub.conf.new
    cat /etc/grub.conf | head -24 |  grep -v splashimage > /root/grub.conf.new
    /bin/rm -rf /boot/grub/grub.conf
    mv /root/grub.conf.new /boot/grub/grub.conf
fi
# 配置snmp
snmp_install(){
    echo "dlmod cmaX /usr/lib/libcmaX.so
    dlmod cmaX /usr/lib64/libcmaX64.so
    rocommunity  360buy 0.0.0.0/0

    com2sec notConfigUser  default          360buy
    group   notConfigGroup v1               notConfigUser
    group   notConfigGroup v2c              notConfigUser

    view systemview included .1
    view systemview included .1.3.6.1.2.1.25.1
    access notConfigGroup "" any noauth exact systemview none none
    trapcommunity 360buy
    trapsink default
    syslocation Unknown
    realStorageUnits 0
    ">/etc/snmp/snmpd.conf
cat > /etc/sysconfig/snmpd <<EOF 
OPTIONS="-LS 2 d -Lf /dev/null -p /var/run/snmpd.pid -a"
EOF
    chkconfig snmpd on
    service snmpd start
}
snmp_install

# 设置用户
setUser(){
groupadd -g 600 hadp   
useradd -u 600 -g 600  hadp
mkdir -p /software/servers
chown -R hadp:hadp /software/
mkdir /home/hadp/bin
cd /home/hadp/bin
chown hadp:hadp /etc/hosts
}
setUser

# 设置安全rm
#cd /software
#mkdir -p /data0/.trash
echo "alias rm='mv -f --target-directory=/data0/.trash/'" >> /etc/bashrc
source /etc/bashrc
chmod 777 /data0/.trash
#mkdir /data0/.trash
#echo "alias rm='mv -f --target-directory=/data0/.trash/'" >> /etc/bashrc
#source /etc/bashrc
#chmod 757 /data0/.trash

# 设置umask
#echo "umask 027" >>/etc/profile

# 删除不用的用户
user_nohelp_del(){
for i in `cat /etc/passwd | sort |awk -F ":" '{print $1}'`; do
case $i in
lp |news |uucp |games |mail)
userdel $i
groupdel $i
;;
*)
;;
esac
done
}
user_nohelp_del

# 配置history
cat >> /etc/profile <<EOF
export TMOUT=900
HISTTIMEFORMAT="%Y/%m/%d/%H-%M-%s #>"
export=HISTTIMEFORMAT
EOF
source /etc/profile

# 配置安全ssh
#sed -i "s/#PermitEmptyPasswords no/PermitEmptyPasswords no/g" /etc/ssh/sshd_config

# 配置 libcgroupyum
#CENTOS_RELEASE=`grep Final /etc/issue|awk '{print $3}'`
CENTOS_RELEASE=`cat /etc/redhat-release |awk -F "release" '{print $2}'|awk  -F '' '{OFS="";print $2,$3,$4}'`
cd /etc/yum.repos.d/
mkdir backup
mv *.repo ./backup
#wget http://172.22.99.122/iso/CentOS-6.3-Base.repo
wget http://mirrors.jd.local/CentOS/repo/CentOS-${CENTOS_RELEASE}-Base.repo
# 配置i18n
#echo 'LANG="zh_CN.UTF-8"
#SYSFONT="latarcyrheb-sun16"' > /etc/sysconfig/i18n

# 配置hostname
#HOSTNAM_IN=`grep IPA /etc/sysconfig/network-scripts/ifcfg-eth0 |awk -F. '{print $3$4}'`
#HOSTNAM_IN=`ip addr sh|grep -v 'global secondary'|grep inet|grep -v 169.254|grep -v inet6|grep -v '127.0.0.1'|awk '{print $2}'|awk -F'/' '{print $1}'|head -n 1|awk -F"." '{print $3$4}'`
#HOSTNAME_IN="BJ-YZH-1-H1-$HOSTNAM_IN.jd.com"
#echo $HOSTNAME_IN
#echo "NETWORKING=yes
#NETWORKING_IPV6=no
#HOSTNAME=$HOSTNAME_IN" >/etc/sysconfig/network
#hostname $HOSTNAME_IN
#echo "search 360buy.com
#nameserver 172.17.1.134
#nameserver 192.168.143.86
#nameserver 202.106.0.20">/etc/resolv.conf

# 关闭内存整理
#echo never > /sys/kernel/mm/redhat_transparent_hugepage/defrag
#echo "echo never > /sys/kernel/mm/redhat_transparent_hugepage/defrag" >> /etc/rc.d/rc.local

# 配置limits
#touch /etc/security/limits.d/90-nofile.conf
#touch /etc/security/limits.d/90-stack.conf
#cat > /etc/security/limits.d/90-nofile.conf <<EOF
#* soft nofile 65535
#* hard nofile 65535
#EOF
#cat > /etc/security/limits.d/90-nproc.conf <<EOF
#* soft nproc 65535
#* hard nproc 65535
#EOF
#cat > /etc/security/limits.d/90-stack.conf <<EOF
#* soft stack 65535
#* hard stack 65535
#EOF

# 配置ntp，放在host配置后面
echo "$[$RANDOM % 50 + 5] * * * * sleep $[$RANDOM % 50 + 5];/usr/sbin/ntpdate ntp.jd.com;/sbin/hwclock -w" > /var/spool/cron/root
/usr/sbin/ntpdate ntp.jd.com;/sbin/hwclock -w

# 安装软件
if [ $server_release == 7 ];then
    yum -y install lzo lzop expect glibc mysql lftp libcgroup libcgroup-tools net-snmp-python
    systemctl enable cgconfig.service
    systemctl enable cgred.service
else
    yum -y install lzo-devel lzop expect glibc.i686 mysql lftp libcgroup net-snmp-python
    chkconfig cgconfig on
    chkconfig cgred on
fi
cd /home/hadp/bin
wget http://172.22.99.122/iso/download.sh
wget http://172.22.99.122/iso/package_install.sh
sh download.sh
sh package_install.sh

# 分区格式化
fdiskMkfs_1(){
if [ `cat /etc/fstab | grep sdb | wc -l` -gt 0 ]; then
echo '分区已经存在，程序终止！'
exit
fi

if [ -d /data0 ]; then
i=1
n=1
else
i=0
n=0
fi
for dev in `ls /dev/sd? | grep -v sda`; do
devNum=$dev"1"
dir="/data"$i
((i=i+1))

mkdir -p $dir

parted -s $dev mklabel gpt
parted -s $dev mkpart primary 1 100%
mkfs.ext4 -T largefile $devNum &

done

#格式化后重启服务器
wait

sleep 60

ls -l /dev/disk/by-uuid/ >> /root/setup.log

#i=1
for dev in `ls /dev/sd? | grep -v sda|awk -F"/" '{print $3}'`; do
uuid=`ls -l /dev/disk/by-uuid/|grep $dev|awk '{print $9}'`
dir="/data"$n
((n=n+1))
echo "UUID=$uuid $dir ext4 defaults 1 2">>/etc/fstab
done
mount -a
mkdir -p -m 777 /data0/.trash
reboot
}

fdiskMkfs_2(){
if [ `cat /etc/fstab | grep sdb | wc -l` -gt 0 ]; then
echo '分区已经存在，程序终止！'
exit
fi

i=0
for dev in `ls /dev/sd? | grep -v sdm`; do
devNum=$dev"1"
dir="/data"$i
((i=i+1))

mkdir -p $dir

parted -s $dev mklabel gpt
parted -s $dev mkpart primary 1 100%
mkfs.ext4 -T largefile $devNum &

done

#格式化后重启服务器
wait

sleep 60

ls -l /dev/disk/by-uuid/ >> /root/setup.log

i=0
for dev in `ls /dev/sd? | grep -v sdm|awk -F"/" '{print $3}'`; do
uuid=`ls -l /dev/disk/by-uuid/|grep $dev|awk '{print $9}'`
dir="/data"$i
((i=i+1))
echo "UUID=$uuid $dir ext4 defaults 1 2">>/etc/fstab
done
mount -a
mkdir -p -m 777 /data0/.trash
reboot
}
#if (ls /dev/sd* |grep sda1 &>/dev/null)
#then
#   fdiskMkfs_1
#else
#  fdiskMkfs_2
#fi
