#!/bin/bash

passwd='0o0o0o0o'
expect << EOF
spawn ssh wangdelong5@jps.jd.com -p 80
expect {
    "*password:" {   
        send "$passwd\r"; 
    }
}
EOF
