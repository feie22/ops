#!/usr/bin/expect
spawn ssh root@172.16.110.9

expect {
	"yes/no" { send "yes\r"; exp_continue}
	"password:" { send "1\r"};
}
interact
