#!/usr/bin/env python
#-*- coding:utf8 -*-

import os
import simplejson as json
from subprocess import Popen, PIPE
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource

from gevent.threadpool import ThreadPool
import multiprocessing

pool = ThreadPool(multiprocessing.cpu_count() - 1)

port = 8080
log_file = '/data/logs/playbook.log'

if not os.path.isdir(os.path.dirname(log_file)):
    os.makedirs(os.path.dirname(log_file), 0777)

import logging.handlers
mylggr = logging.getLogger(__name__)
mylggr.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(log_file,
                                               mode='a+',
                                               maxBytes=100*1024*1024,#Bytes
                                               backupCount=5)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)-8s[%(filename)s:%(lineno)d(%(funcName)s)] %(message)s'))
mylggr.addHandler(handler)


def do_task(**post_data):
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

    mylggr.debug('hosts %s playbook %s run stdout %s ,stderr %s!' %
                 (hosts, playbook, stdout, stderr))
    return {'hosts': hosts,
            'playbook': playbook,
            'stdout': stdout,
            'stderr': stderr,
            'returncode': rc}


class PlaybookApplication(WebSocketApplication):
    def on_open(self):
        print "Connection opened"

    def on_message(self, message):
        response = dict(version=1.0, code=200, message="", value="")
        message = json.loads(message)
        response['code'] = 200
        response['message'] = u"任务已收到 正在执行 请稍候 具体执行日志在" + log_file
        response['value'] = pool.apply(do_task, kwds=message)
        self.ws.send(json.loads(response))

    def on_close(self, reason):
        print reason


WebSocketServer(('', port),
                Resource({'/': PlaybookApplication})).serve_forever()
