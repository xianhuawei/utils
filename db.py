#!/usr/bin/env python
# -*- coding:utf8 -*-

import MySQLdb
from DBUtils.PooledDB import PooledDB
import logging
import time

try:
    import MySQLdb.constants
    import MySQLdb.converters
    import MySQLdb.cursors
except ImportError:
    logging.error("MySQLdb is not install ")


class Row(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


class DB(object):
    def __init__(self, **kwargs):
        self.host = kwargs.get('host')
        self.database = kwargs.get('db')
        self.max_idle_time = float(7 * 3600)

        args = dict(conv=MySQLdb.converters.conversions,
                    use_unicode=True,
                    charset="utf8",
                    connect_timeout=0,
                    sql_mode="TRADITIONAL",
                    **kwargs)
        self.con = None
        self._db = None
        self._last_use_time = time.time()
        self.pool = PooledDB(creator = MySQLdb,
                             mincached = 6,      # minimum connections
                             maxcached = 60,     # maximum connections
                             maxshared = 0,       # max shared connections. 0 not share
                             maxusage = 0,        # max use times. o not limited
                             **args)
        if self.con == None:
            self.con = self.pool.connection()
            self.cur = self.con._con.cursor()
            self._db = self.con._con

    def close(self):
        self.con._con.close()
        self.cur.close()
        self.con = None

    def reconnect(self):
        self.con._con.close()
        self.cur.close()
        self.con = None
        self.con = self.pool.connection()
        self._db.autocommit(True)

    def iter(self, query, *parameters, **kwparameters):
        self._ensure_connected()
        try:
            self._execute(self.cur, query, parameters, kwparameters)
            column_names = [d[0] for d in self.cur.description]
            for row in self.cur:
                yield Row(zip(column_names, row))
        finally:
            self.cur.close()

    def query(self, query, *parameters, **kwparameters):
        try:
            self._execute(self.cur, query, parameters, kwparameters)
            column_names = [d[0] for d in self.cur.description]
            return [Row(zip(column_names, row)) for row in self.cur]
        finally:
            self.cur.close()

    def get(self, query, *parameters, **kwparameters):
        rows = self.query(query, *parameters, **kwparameters)
        if not rows:
            return None
        elif len(rows) > 1:
            raise Exception("Multiple rows returned for Database.get() query")
        else:
            return rows[0]

    def execute(self, query, *parameters, **kwparameters):
        return self.execute_lastrowid(query, *parameters, **kwparameters)

    def execute_lastrowid(self, query, *parameters, **kwparameters):
        cursor = self._cursor()
        try:
            self._execute(cursor, query, parameters, kwparameters)
            return cursor.lastrowid
        finally:
            cursor.close()

    def execute_rowcount(self, query, *parameters, **kwparameters):
        try:
            self._execute(self.cur, query, parameters, kwparameters)
            return self.cur.rowcount
        finally:
            self.cur.close()

    def executemany(self, query, parameters):
        return self.executemany_lastrowid(query, parameters)

    def executemany_lastrowid(self, query, parameters):
        try:
            self.cur.executemany(query, parameters)
            return self.cur.lastrowid
        finally:
            self.cur.close()

    def executemany_rowcount(self, query, parameters):
        try:
            self.cur.executemany(query, parameters)
            return self.cur.rowcount
        finally:
            self.cur.close()

    update = delete = execute_rowcount
    updatemany = executemany_rowcount

    insert = execute_lastrowid
    insertmany = executemany_lastrowid

    def _ensure_connected(self):
        if (self._db is None or
            (time.time() - self._last_use_time > self.max_idle_time)):
            self.reconnect()
        self._last_use_time = time.time()

    def _cursor(self):
        self._ensure_connected()
        return self._db.cursor()

    def _execute(self, cursor, query, parameters, kwparameters):
        try:
            return cursor.execute(query, kwparameters or parameters)
        except IOError:
            logging.error("Error connecting to MySQL on %s", self.host)
            self.con._con.close()
            raise


if __name__ == '__main__':
    import config
    db = DB(**config.db)
    rows = db.query("select * from EMPLOYEE")

    for row in rows:
        print(row)
    print(rows)
