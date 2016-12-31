将需要操作的云主机的ip，ssh的端口，和root账号的密码写到hosts.txt文件中，每一行代表一个主机

比如

10.0.0.1 22 my_password

然后执行 

./batch-mkfs.py

如果用户想自己在云主机的shell中执行相同的操作，请直接在shell里输入如下命令：

if grep -q /data /etc/fstab ; then uuid=notneed; echo /data already in fstab; else uuid=`mkfs.ext3 /dev/vdb > /dev/null 2>&1 && blkid /dev/vdb | awk '{print $2}'`;fi;if [[ $uuid == UUID* ]]; then echo $uuid /data ext3 noatime,acl,user_xattr 1 0 >> /etc/fstab; mount -a; else echo mkfs failed; fi;
