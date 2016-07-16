#!/usr/bin/env python
# -*- coding:utf8 -*-

import hashlib
import redis
import simplejson as json
import functools


class Cache(object):
    def __init__(self, **kwargs):
        self.pool = redis.ConnectionPool(**kwargs)
        self.redis = redis.StrictRedis(connection_pool=self.pool)

    def get_cache_key(self, prefix, tpl, func, *args, **kwargs):
        def md5(input):
            m2 = hashlib.md5()
            m2.update(input)
            return str(m2.hexdigest())

        key = (prefix, '$', tpl, '$', str(func), tuple(args), str(kwargs))
        return prefix + '_' + md5(str(key))

    def cache(self, prefix='', ttl=3600, key='', op='select'):
        def handle_func(func):
            @functools.wraps(func)
            def handle_args(*args, **kwargs):
                ckey = self.get_cache_key(prefix, key, func, *args, **kwargs)
                if op == 'select':
                    obj = self.redis.get(ckey)
                    if obj == None:
                        result = func(*args, **kwargs)
                        self.redis.set(ckey, json.dumps(result), ttl)
                        return result
                    else:
                        return json.loads(obj)
                elif op == 'del' or op == 'delete' or op == 'remove':
                    self.redis.delete(ckey)
                elif op == 'insert' or op == 'update':
                    result = func(*args, **kwargs)
                    self.redis.set(ckey, json.dumps(result), ttl)
                    return result

            return handle_args

        return handle_func


if __name__ == '__main__':
    import config
    cache = Cache(**config.redis_conf)

    @cache.cache(prefix='test_auto_cache', ttl=3600, key='#p[id],#p[name]')
    def test_auto_cache(id=0, name='hello'):  #auto cache result
        return db.query("select * from test where id=%s and name = %s" %
                        (id, name))
