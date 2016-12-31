#!/usr/bin/expect
spawn ssh root@172.16.100.128

expect {
	"yes/no" { send "yes\r"; exp_continue}
	"password:" { send "000\r"};
}
interact
