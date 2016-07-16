#!/usr/bin/env python
# -*- coding:utf8 -*-

import os
from gevent.threadpool import ThreadPool
from gevent.wsgi import WSGIServer
import subprocess
from subprocess import Popen, PIPE
import simplejson as json
import multiprocessing
import requests
import hashlib
import cgi
from cStringIO import StringIO

accept_key = 'MOH134fnonf'  #服务端 客户端加密校验key
callback_url = ''  #回调url

port = 8080
log_file = '/data/logs/playbook.log'

import logging.handlers
mylggr = logging.getLogger(__name__)
mylggr.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(log_file,
                                               mode='a+',
                                               maxBytes=1073741824,#1G
                                               backupCount=5)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)-8s[%(filename)s:%(lineno)d(%(funcName)s)] %(message)s'))
mylggr.addHandler(handler)

if not os.path.isdir(os.path.dirname(log_file)):
    os.makedirs(os.path.dirname(log_file), 0777)

task_pool = ThreadPool(multiprocessing.cpu_count() - 1)
callback_pool = ThreadPool(multiprocessing.cpu_count() - 1)


def do_task(**post_data):
    callback = post_data.get('callback_url', callback_url)
    acceptkey = post_data.get('accept_key', accept_key)
    task_id = post_data.get('task_id', 0)
    playbook = post_data.get('playbook', '')
    extra_vars = post_data.get('extra_vars', '')
    hosts = post_data.get('hosts', '127.0.0.1,')
    p = Popen("/usr/bin/ansible-playbook -i %s  %s --extra-vars='%s' -s" %
              (hosts, playbook, extra_vars),
              shell=True,
              stdout=PIPE,
              stderr=PIPE)
    try:
        stdout, stderr = p.communicate()
    finally:
        subprocess._cleanup()
        p.stdout.close()
        p.stderr.close()
    rc = p.returncode

    mylggr.debug(
        'task id  %d in hosts %s playbook %s return stdout %s ,stderr %s!' %
        (task_id, hosts, playbook, stdout, stderr))
    return {'task_id': task_id,
            'callback_url': callback,
            'accept_key': acceptkey,
            'hosts': hosts,
            'playbook': playbook,
            'stdout': stdout,
            'stderr': stderr,
            'returncode': rc}


#change task status & insert log
def callback_post(**result):
    callback_url = result.get('callback_url')
    if not callback_url:
        return
    headers = {'content-type': 'application/json'}
    m1 = hashlib.md5()
    accept_key = result.get('accept_key')
    m1.update(accept_key + str(result['task_id']))
    result['access_token'] = m1.hexdigest()
    r = requests.post(callback_url, data=json.dumps(result), headers=headers)
    mylggr.debug("callback %s  data %s return %s" %
                 (callback_url, json.dumps(result), r.text))
    r.close()


def callback(callback_result):
    callback_pool.apply_async(callback_post, kwds=callback_result)


def application(environ, start_response):
    status = '200 OK'

    headers = [('Content-Type', 'application/json')]

    start_response(status, headers)
    result = {
        'code': 200,
        'message':
        'task receive wait a moment to change task status & insert log'
    }
    a = {}
    if environ['REQUEST_METHOD'] in ['POST', 'PUT']:
        if environ.get('CONTENT_TYPE', '').lower().startswith('multipart/'):
            fp = environ['wsgi.input']
            a = cgi.FieldStorage(fp=fp, environ=environ, keep_blank_values=1)
        else:
            fp = StringIO(environ.get('wsgi.input').read())
            a = cgi.FieldStorage(fp=fp, environ=environ, keep_blank_values=1)
    else:
        a = cgi.FieldStorage(environ=environ, keep_blank_values=1)

    post_data = {}
    for key in a.keys():
        post_data[key] = a[key].value
    mylggr.debug('request : ip %s , post_data %s ' %
                 (environ.get('REMOTE_ADRR'), str(post_data)))
    task_pool.apply_async(do_task,
                          kwds=json.loads(post_data),
                          callback=callback)
    #sync
    #result = task_pool.apply(do_task,kwds=json.loads(post_data))
    #return [json.dumps(result)]
    yield json.dumps(result) + '\n'


WSGIServer(('', port), application).serve_forever()
