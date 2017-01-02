#!/bin/bash
# configuration LDAP server 
# RHEL6
# install software
yum -y install openldap* db4* migrationtools nfs-utils rpcbind

#========================== create ldapuser and generate ldif ========================
ldapuser_passwd=password
if [ ! -d /home/guests ];then
	mkdir -p /home/guests
fi

/usr/sbin/useradd -u 6000 test002

for i in $(seq 1 10)
do
	/usr/sbin/useradd ldapuser$i -d /home/guests/ldapuser$i
	echo $ldapuser_passwd | /usr/bin/passwd --stdin ldapuser$i
done

cd /usr/share/migrationtools/
sed -i '71s/padl/domain40.example/' migrate_common.ph
sed -i '74s/padl/domain40,dc=example/' migrate_common.ph
./migrate_base.pl > base.ldif
grep ldapusers /etc/group > group.in
./migrate_group.pl group.in > group.ldif
grep ldapuser /etc/passwd > user.in
./migrate_passwd.pl user.in > user.ldif

#=========================== configuration LDAP Server ===============================
cp /usr/share/openldap-servers/slapd.conf.obsolete /etc/openldap/slapd.conf
cp /usr/share/openldap-servers/DB_CONFIG.example /var/lib/ldap/DB_CONFIG
mv /etc/openldap/slapd.d/  /etc/openldap/slapd
sed -i '/dc=my-domain/s/dc=my-domain/dc=domain40,dc=example/' /etc/openldap/slapd.conf
pwd="rootpw        `slappasswd -h {SSHA} -s redhat`"
sed -i "123a$pwd"  /etc/openldap/slapd.conf


#============================== start slapd =========================================
service slapd start
chkconfig slapd on

#============================== import ldif =========================================
ldapadd -D "cn=Manager,dc=domain40,dc=example,dc=com" -w redhat -f base.ldif
ldapadd -D "cn=Manager,dc=domain40,dc=example,dc=com" -w redhat -f group.ldif
ldapadd -D "cn=Manager,dc=domain40,dc=example,dc=com" -w redhat -f user.ldif

#============================== export HOME =========================================
echo "/home/guests	*(rw,sync)" >> /etc/exports
service rpcbind restart
service nfs restart
chkconfig rpcbind on
chkconfig nfs on

service iptables stop
setenforce 0









