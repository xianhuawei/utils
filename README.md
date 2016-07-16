# todo
    python-pillow.rpm generator
# 安装常用软件

    yum install -y thrift protobuf python-pip  MySQL-python python-thrift scipy numpy python-pandas python-gevent python-lxml python-gunicorn python-simplejson leveldb python-mprpc python-msgpack

    pip install redis redis-shard  kazoo falcon requests theano keras dbutils grequests gsocketpool geventconnpool gevent_etcd geventcron geventhttpclient ansible schedule algorithms protobuf-to-dict pyroute2 xmltodict tushare fabric fabric-gunicorn python-actors kafka-python lggr peewee html5lib beautifulsoup4 retrying
  
    tensorflow https://github.com/tensorflow/tensorflow

# 自动生成model
        python -m pwiz -e mysql -uroot -H127.0.0.1 -p3306 myschema >myschema.py #myschema 项目的db名 -e 可选mysql postresql

# 生成多端口并启动,输出nginx upstream
    port=8080
    filename=web_task
    cpu_count=`python -c "import multiprocessing;print multiprocessing.cpu_count()-2"`
    for i in $(seq 0 $cpu_count); do item=$(($port+$i));sed -e "s/$port/$item/g" ./$filename.py>$filename$item.py;nohup python ./$filename$item.py >/dev/null&;done
    for i in $(seq 0 $cpu_count); do item=$(($port+$i));echo "server 127.0.0.1:$item";done

# 默认启动多进程
        gunicorn -c gunicorn.conf
# mysql utils
        https://github.com/pinterest/mysql_utils

# cache db使用
        配置config.py
        # cache
        import config
        cache = Cache(**config.redis_conf)
    
        @cache.cache(prefix='test_auto_cache',ttl=3600,key='#p[id],#p[name]')
        def test_auto_cache(id=0,name='hello'): #auto cache result
            return '33333'
        
        # db 
            import config
            db = DB(**config.db)
            rows = db.query("select * from EMPLOYEE")
        
            for row in rows:
                print(row)
            print(rows)
        
        # webpy db
            from webpy_db import database
            db1 = database(dbn='mysql', db='dbname1', user='foo', pw='')
            db2 = database(dbn='mysql', db='dbname2', user='foo', pw='')
        
            print db1.select('foo', where='id=1')
            print db2.select('bar', where='id=5')
            entries = db.select('mytable')
            myvar = dict(name="Bob")
            results = db.select('mytable', myvar, where="name = $name")
            results = db.select('mytable', what="id,name")
            results = db.select('mytable', where="id>100")
            results = db.select('mytable', order="post_date DESC")
            results = db.select('mytable', group="color") 
            results = db.select('mytable', limit=10) 
            results = db.select('mytable', offset=10) 
            results = db.select('mytable', offset=10, _test=True) 
            
            
            db.update('mytable', where="id = 10", value1 = "foo")
            
            db.delete('mytable', where="id=10")
            
            sequence_id = db.insert('mytable', firstname="Bob",lastname="Smith")
            
            t = db.transaction()
            try:
                db.insert('person', name='foo')
                db.insert('person', name='bar')
            except:
                t.rollback()
                raise
            else:
                t.commit()
            
            with db.transaction():
              db.insert('person', name='foo')
              db.insert('person', name='bar')
        
        # shard
            from shard import db
            
            import datetime
            import unittest
        
            class Comment(object):
        
                def __str__(self):
                    return str(self.__dict__)
        
            class Test(unittest.TestCase):
        
        
                def testInsert(self):
                        comment = Comment()
                        comment.object_id, comment.user_id = 100000, 1000
                        comment.updated, comment.body = datetime.datetime.now(), 'Hello, world!'
                        db.comment.insert(model=comment,shard=comment.user_id)
        
                def testQueryOne(self):
                        comment = db.comment.query_one(clazz=Comment,
                                                       where='user_id=$user_id', vars={'user_id':1000}, shard=1000)
                        print ">>>>>>> Comment:", comment
        
                def testQueryList(self):
                        comments = db.comment.query_list(clazz=Comment,
                                                         where='user_id=$user_id', vars={'user_id':1000}, shard=1000)
                        print ">>>>>>>>>>> Comments <<<<<<<<<<<<<<<"
                        for comment in comments:
                            print comment
        
                def testDelete(self):
                        db.comment.delete(table='comment', where='user_id=$user_id', vars={'user_id':1000}, shard=1000)
        
        
            class User(object):
        
                def __str__(self):
                    return str(self.__dict__)
        
            class Student(object):
        
                def __str__(self):
                    return str(self.__dict__)
        
            class Test(unittest.TestCase):
        
                def testBasicQueryOne(self):
                    user = db.user.query_one(clazz=User, table='users', where='id=$id', vars={'id':283})
                    print user
        
                def testBasicQueryList(self):
                    user_list = db.user.query_list(clazz=User, table='users', offset=0, limit=10)
                    for user in user_list:
                        print '>>> user:', user
        
                def testInsert(self):
                    std = Student()
                    std.name, std.age, std.score = 'Sam', 23, 100
                    print '>>>> gen Id:', db.test.insert(model=std)
        
                def testMultiInsert(self):
                    records = []
                    records.append({'name':'Sam', 'age':23, 'score':100})
                    records.append({'name':'Jack', 'age':25, 'score':90})
                    records.append({'name':'Nick', 'age':30, 'score':50})
                    db.test.multi_insert('student', records)
        
                def testDelete(self):
                    db.test.delete(table='student', where='name=$name', vars={'name':'Sam'})
        
                def testUpdate(self):
                    student = db.test.query_one(clazz=Student, where='id=$id', vars={'id':5})
                    student.name = u'迟宏泽'
                    db.test.update(model=student)
        
                def testQuery(self):
                    csr = db.test.query(sql='select name from student')
                    print '>>>>>>>> Test Free Query <<<<<<<<<<<'
                    for row in csr:
                        print "----> name:", row['name']
        
                def testQueryOneField(self):
                    print '>>>>>> Count:', db.test.query_one_field(what='count(1) as c',
                                                                   table='student', field='c')
        
                def testQueryFieldList(self):
                    print '>>>>>>> Name List:'
                    name_list = db.test.query_field_list(what='name', table='student')
                    for name in name_list:
                        print ">>>>>> Name:", name
        
# 搭建pypi私有源
        #pip源机器
        pip install pip2pi
        mkdir -p /data/pypi

        echo '[global]
        index-url = http://pypi.douban.com/simple' >~/.pip/.pip.conf

        #批量同步
        pip2tgz /data/pypi -r ./requirements.txt

        #建索引
        dir2pi /data/pypi

        #把/data/pypi 配置成web 对外访问
        
        #目标机器使用私有源
        echo '[global]
        index-url = http://your_host_ip/pypi/simple'>~/.pip/.pip.conf

