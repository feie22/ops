#!/usr/bin/expect
set ip 172.16.100.128
set password 000
set timeout 10

spawn ssh root@$ip

expect {
	"yes/no" { send "yes\r"; exp_continue}
	"password:" { send "$password\r"};
}
interact
