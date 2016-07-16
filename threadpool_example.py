#!/usr/bin/env python
# -*- coding:utf8 -*-


import urllib2 

urls = [
    'http://www.python.org', 
    'http://www.python.org/about/',
    'http://www.onlamp.com/pub/a/python/2003/04/17/metaclasses.html',
    'http://www.python.org/doc/',
    'http://www.python.org/download/',
    'http://www.python.org/getit/',
    'http://www.python.org/community/',
    'https://wiki.python.org/moin/',
    'http://planet.python.org/',
    'https://wiki.python.org/moin/LocalUserGroups',
    'http://www.python.org/psf/',
    'http://docs.python.org/devguide/',
    'http://www.python.org/community/awards/'
    ]
#高io同步用线程池
from multiprocessing.dummy import Pool as ThreadPool 
pool = ThreadPool()
results = pool.map(urllib2.urlopen, urls)
pool.close() 
pool.join()

def test(url):
    res = urllib2.urlopen(url)
    return res.read()

#高io同步用线程池
from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing
pool = ThreadPool(multiprocessing.cpu_count())
results = pool.map_async(test, urls)
pool.close()
pool.join()

print results.wait(timeout=10)
print results.successful()
print results.ready()
for item in results.get(timeout=10):
    print item
    
