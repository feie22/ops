#!/usr/bin/env python
#coding=utf-8
__author__ = 'anbaoyong'

#===============================================================================
#         FILE: setup.py
#  DESCRIPTION: saltapi
#       AUTHOR: anbaoyong
#      VERSION: 1.0
#      CREATED: 2015-12-02
#===============================================================================


import urllib2, urllib, json, re


class saltAPI:
    def __init__(self):
        self.__url = 'http://172.19.185.84:8181'    
        self.__user =  'salt'             
        self.__password = 'MXBe59Mpr0{G>!!$N.E{X4X#j'      
        self.__token_id = self.salt_login()
 
    def salt_login(self):
        params = {'eauth': 'pam', 'username': self.__user, 'password': self.__password}
        encode = urllib.urlencode(params)
        obj = urllib.unquote(encode)
        headers = {'X-Auth-Token':''}
        url = self.__url + '/login'
        req = urllib2.Request(url, obj, headers)
        opener = urllib2.urlopen(req)
        content = json.loads(opener.read())
        try:
            token = content['return'][0]['token']
            return token
        except KeyError:
            raise KeyError
 
    def postRequest(self, obj, prefix='/'):
        url = self.__url + prefix
        headers = {'X-Auth-Token'   : self.__token_id}
        req = urllib2.Request(url, obj, headers)
        opener = urllib2.urlopen(req)
        content = json.loads(opener.read())
        # print content
        return content['return']

    def saltCmd(self, params):
        obj = urllib.urlencode(params)
        obj, number = re.subn("arg\d", 'arg', obj)
        res = self.postRequest(obj)
        return res

sapi = saltAPI()

def main(params):
    dic = {'client':'local', 'expr_form': 'list'}
    params.update(dic)
    ret = sapi.saltCmd(params)
    return ret


def main_async(params):
    dic = {'client': 'local_async', 'expr_form': 'list'}
    params.update(dic)
    ret = sapi.saltCmd(params)
    return ret


def main_job(jid):
    prefix = "/jobs/" + jid
    ret = sapi.postRequest(None, prefix)
    return ret


def main_key(ip_list):
    params = {'client': 'wheel', 'expr_form': 'list', 'match':','.join(ip_list), 'fun':'key.delete'}
    ret = sapi.saltCmd(params)
    return ret


if __name__ == '__main__':
    #params = json.loads(sys.argv[1])
    #params = {'fun': 'HbaseConf.hadoop_conf','tgt': '172.17.46.11,172.17.46.102,172.17.46.103', 'arg1': 'aby_test','arg2':'449]'}
    params = {'fun': 'saltutil.sync_all','tgt': '172.19.186.100,172.19.186.101,172.19.186.102,172.19.186.103,172.19.186.104,172.19.186.105,172.19.186.106,172.19.186.87,172.19.186.88,172.19.186.89,172.19.186.90,172.19.186.91,172.19.186.93,172.19.186.94,172.19.186.95,172.19.186.96,172.19.186.97,172.19.186.98,172.19.186.99'}

    main(params)
