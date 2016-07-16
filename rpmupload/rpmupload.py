#!/bin/env python
#coding: utf8

import os
import glob
import sys
import requests

cobbler_ip = ['1.1.1.1','2.2.2.2','3.3.3.3']

def post_file(file):
    for ip in cobbler_ip.split(','):
        files = {'upfile': open(file, 'rb')}
        filepath,filename = os.path.split(file)
        r = requests.post('http://'+ip+':8080', files=files,data={'filename':filename})

path = ''
try:
    path = sys.argv[1]
except:
    pass
if not path:
    print u"\n\n上传rpm包到私有yum库\n\n使用方法 rpmupload.py rpmdir \n\n\t rpmupload.py rpmfile\n\n"
else:
    if os.path.isdir(path):
        for rpmfile in glob.glob(path+'/*.rpm'):
            post_file(rpmfile)
    else:
        post_file(path)

