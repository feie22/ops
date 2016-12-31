#!/usr/bin/env python
import os


def get_ip_and_passwd(fpath):
    return map(str.split, open(fpath).read().strip().split('\n'))


def main():
    fpath = './hosts.txt'
    for line in get_ip_and_passwd(fpath):
        if not line:
            continue
	ip, port, passwd = line
        print 'mkfs for host[%s]' % ip
        os.system('./mkfs-vdb.exp %s %s %s' % (ip, port, passwd))


if __name__ == '__main__':
    main()
