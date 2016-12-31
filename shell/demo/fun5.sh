#!/bin/bash
info() {
        if [ -f /etc/zhuzhu ];then
                echo 100
        else
                echo 200
        fi
        return 50
}

res=$(info)
echo "state: $?"
echo "res: $res"
