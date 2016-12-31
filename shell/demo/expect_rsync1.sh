#!/usr/bin/expect
set ip [lindex $argv 0]
set password [lindex $argv 1]
set timeout 10

spawn rsync -va /etc root@$ip:/tmp

expect {
	"yes/no" { send "yes\r"; exp_continue}
	"password:" { send "$password\r"};
}

expect eof
