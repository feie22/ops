#!/bin/bash

#判断是否有hadoop程序在运行
if [ `su hadp -c 'jps' | wc -l` -gt 1 ];then
    echo 'hadoop is running！'
    exit 1
fi

# 下次启动不执行
sed -i '/hadoop/d' /etc/rc.d/rc.local

server_release=`cat /etc/redhat-release |awk -F "release" '{print $2}'|awk  -F '' '{OFS="";print $2}'`

# 配置 yum 修改yum源
#CENTOS_RELEASE=`grep Final /etc/issue|awk '{print $3}'`
#CENTOS_RELEASE=`cat /etc/redhat-release |awk -F "release" '{print $2}'|awk  -F '' '{OFS="";print $2,$3,$4}'`
cd /etc/yum.repos.d/
mkdir backup
mv *.repo ./backup
wget http://172.22.99.122/iso/CentOS-JD.repo
#wget http://mirrors.jd.local/CentOS/repo/CentOS-${CENTOS_RELEASE}-Base.repo

# 配置sysctl 修改为替换
cat > /etc/sysctl.conf <<EOF
# Kernel sysctl configuration file for Red Hat Linux
#
# For binary values, 0 is disabled, 1 is enabled.  See sysctl(8) and
# sysctl.conf(5) for more details.

# Controls IP packet forwarding
net.ipv4.ip_forward = 0

# Controls source route verification
net.ipv4.conf.default.rp_filter = 1

# Do not accept source routing
net.ipv4.conf.default.accept_source_route = 0

# Controls the System Request debugging functionality of the kernel
kernel.sysrq = 0

# Controls whether core dumps will append the PID to the core filename.
# Useful for debugging multi-threaded applications.
kernel.core_uses_pid = 1

# Controls the use of TCP syncookies
net.ipv4.tcp_syncookies = 1

# Disable netfilter on bridges.
net.bridge.bridge-nf-call-ip6tables = 0
net.bridge.bridge-nf-call-iptables = 0
net.bridge.bridge-nf-call-arptables = 0

# Controls the default maxmimum size of a mesage queue
kernel.msgmnb = 65536

# Controls the maximum size of a message, in bytes
kernel.msgmax = 65536

# Controls the maximum shared segment size, in bytes
kernel.shmmax = 68719476736

# Controls the maximum number of shared memory segments, in pages
kernel.shmall = 4294967296
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
sysctl -p

# 配置vim 增加判断

if [ $server_release == 7 ];then
    wget http://172.22.99.122/iso/molokai.vim -O /usr/share/vim/vim74/colors/molokai.vim    
else
    wget http://172.22.99.122/iso/molokai.vim -O /usr/share/vim/vim72/colors/molokai.vim
fi
if [ `grep molokai /etc/vimrc &> /dev/null ; echo $?` != 0 ];then
    cat >> /etc/vimrc <<EOF
filetype plugin indent on
set pastetoggle=<F9>
set paste
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
set nu
color molokai
EOF
fi

#配置gateone lrz lsz 增加判断
if [ `grep rzsz /etc/bashrc &> /dev/null ; echo $?` != 0 ];then
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
fi
chmod 777 /etc/rzsz.pyc
# 禁用不用的服务 无改动
disable_useless_garbage(){
yum -y install nscd >/dev/null
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
service $CURSRV stop > /dev/null
;;
esac
done
service nscd start
chkconfig nscd on
}
disable_useless_garbage_centos7(){
for i in `ls /etc/systemd/system/multi-user.target.wants/*`; do
CURSRV=`echo $i|cut -c 45-`
#echo $CURSRV
case $CURSRV in
crond.service|network.service|sshd.service|syslog.service|xinetd.service|sysstat.service|snmpd.service|rsyslog.service|nscd.service|cgconfig.service|cgred.service|salt-minion.service|gmond.service)
    #echo "Base services, Skip!"
    ;;
*)
    #echo "change $CURSRV to disable"
    systemctl disable $CURSRV > /dev/null
    systemctl stop $CURSRV > /dev/null
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

# 系统设置 增加判断
set_system_config(){
## ssh设置
_sshd_file=/etc/ssh/sshd_config
sed -i "s/GSSAPIAuthentication yes/GSSAPIAuthentication no/g" $_sshd_file
sed -i "s/#UseDNS yes/UseDNS no/g" $_sshd_file
### 配置安全ssh
sed -i "s/#PermitEmptyPasswords no/PermitEmptyPasswords no/g" /etc/ssh/sshd_config
echo "   StrictHostKeyChecking no" >> /etc/ssh/ssh_config

## 配置i18n
if [ $server_release == 7 ];then
    _lang_file="/etc/locale.conf"
else
    _lang_file="/etc/sysconfig/i18n"
fi
if [ `grep "zh_CN.UTF-8" $_lang_file &> /dev/null ; echo $?` != 0 ];then
    echo 'LANG="zh_CN.UTF-8"
SYSFONT="latarcyrheb-sun16"' > $_lang_file
fi

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
if [ `grep  "echo never" /etc/rc.d/rc.local &> /dev/null ; echo $?` != 0 ];then
    echo "echo never > $_defrag_file" >> /etc/rc.d/rc.local
    echo "echo never > $_enabled_file" >> /etc/rc.d/rc.local
fi

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
if [ `grep 65535 $_limits_file &> /dev/null ; echo $?` != 0 ];then
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
fi
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



# 配置snmp 增加判断
snmp_install(){
    yum -y install net-snmp &> /dev/null
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
if [ `grep snmpd.pid /etc/sysconfig/snmpd &> /dev/null ; echo $?` != 0 ];then
    cat > /etc/sysconfig/snmpd <<EOF 
OPTIONS="-LS 2 d -Lf /dev/null -p /var/run/snmpd.pid -a"
EOF
fi
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

# 设置安全rm 增加判断
#cd /software
#mkdir -p /data0/.trash
if [ `grep "alias rm" /etc/bashrc &> /dev/null ; echo $?` != 0 ];then
    echo "alias rm='mv -f --target-directory=/data0/.trash/'" >> /etc/bashrc
fi
source /etc/bashrc
chmod 777 /data0/.trash

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
if [ `grep HISTTIMEFORMAT /etc/profile &> /dev/null ; echo $?` != 0 ];then
    cat >> /etc/profile <<EOF
export TMOUT=900
HISTTIMEFORMAT="%Y/%m/%d/%H-%M-%s #>"
export=HISTTIMEFORMAT
EOF
fi
source /etc/profile


# 配置ntp，放在host配置后面
echo "$[$RANDOM % 50 + 5] * * * * sleep $[$RANDOM % 50 + 5];/usr/sbin/ntpdate ntp.jd.com;/sbin/hwclock -w" > /var/spool/cron/root
/usr/sbin/ntpdate ntp.jd.com;/sbin/hwclock -w

# 安装软件
if [ $server_release == 7 ];then
    yum -y install lzo lzop expect glibc mysql lftp libcgroup libcgroup-tools net-snmp-python &> /dev/null
    systemctl enable cgconfig.service
    systemctl enable cgred.service
else
    yum -y install lzo-devel lzop expect glibc.i686 mysql lftp libcgroup net-snmp-python &> /dev/null
    chkconfig cgconfig on
    chkconfig cgred on
fi

/bin/rm -rf /software
mkdir /software/servers -p
mkdir -p /software/servers/softwarebak
cd /software/servers
wget http://172.22.99.122/iso/jdk1.6.0_25.tar.gz
wget http://172.22.99.122/iso/jdk1.7.0_67.tar.gz
wget http://172.22.99.122/iso/lzo.tar.gz
wget http://172.22.99.122/iso/Python-3.2.3.tgz
wget http://172.22.99.122/iso/iftop-1.0-0.7.pre4.el6.x86_64.rpm

chown -R hadp.hadp /software/servers

tar -zxf jdk1.6.0_25.tar.gz 
tar -zxf jdk1.7.0_67.tar.gz 

mv jdk1.6.0_25.tar.gz softwarebak
mv jdk1.7.0_67.tar.gz softwarebak
##install lzo
tar -zxf lzo.tar.gz
cd lzo/lzo-2.06
./configure --enable-shared
make&&make install
echo "/usr/local/lib" >/etc/ld.so.conf.d/lzo.conf && /sbin/ldconfig -v
cd ../lzop-1.03
./configure --enable-shared
make&&make install
cd /software/servers
mv lzo.tar.gz softwarebak
##install python
LANG=zh
cd /software/servers
tar -zxf Python-3.2.3.tgz
cd Python-3.2.3
./configure
make
make install
cd /software/servers
mv Python-3.2.3.tgz softwarebak
##install iftop
cd /software/servers
rpm -ivh iftop-1.0-0.7.pre4.el6.x86_64.rpm
/bin/rm -f iftop-1.0-0.7.pre4.el6.x86_64.rpm
