#!/usr/bin/expect
set ip [lindex $argv 0]
set password [lindex $argv 1]
set timeout 10

spawn ssh root@$ip

expect {
	"yes/no" { send "yes\r"; exp_continue}
	"password:" { send "$password\r"};
}
#interact

expect "#"
send "pwd\r"
send "exit\r"

expect eof
