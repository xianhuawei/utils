#coding:utf-8
db = {
    'host': '127.0.0.1',
    'user': 'root',
    'passwd': 'root',
    'database': 'test',
    'charset': 'utf8',
    'maxconnections': 30,
}

redis_conf = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 0,
    'max_connections': 10
}

pool_policy = {
    'default': {
        'maxcached': 20,  # 最大缓存连接数上限
        'maxusage': 0,  # 每个链接的最大允许复用次数,0为没有限制
        'maxconnections': 0,  # 允许的最大链接数量,0为不限制
        'maxshared': 0,  # 最大允许共享的链接数,0为所有链接都属于专用
        'mincached': 10,  #最小缓存链接数,初始化的时候会在池中创建10个链接
        'blocking': 1  # 达到最大链接数量的时候的行为,1为阻塞等待,0为直接返回错误
    },
    'test': {
        'maxcached': 20,
        'maxusage': 0,
        'maxconnections': 0,
        'maxshared': 0,
        'mincached': 10,
        'blocking': 1
    }
}

# name:数据源名称
# write:是否可写
# host:地址
# user:用户名
# pass:密码
# pool_policy:连接池策略
# shard_table:shard的表名基础部分
# shard_begin、shard_end:shard的起始范围

shard = {
    'user_write': {
        "name": "user",
        "write": "true",
        "read": "true",
        "host": "172.4.2.28",
        "user": "test",
        "pw": "ailuntan",
        "db": "ailuntan-center",
        "pool_policy": "default"
    },
    'user_read': {
        "name": "user",
        "write": "false",
        "host": "172.4.2.28",
        "user": "test",
        "pw": "ailuntan",
        "db": "ailuntan-center",
        "pool_policy": "default"
    },
    'test': {
        "name": "test",
        "write": "true",
        "read": "true",
        "host": "172.4.2.28",
        "user": "test",
        "pw": "ailuntan",
        "db": "test",
        "pool_policy": "default"
    },
    'comment': {
        "name": "comment",
        "write": "true",
        "read": "true",
        "host": "172.4.2.28",
        "user": "test",
        "pw": "ailuntan",
        "db": "aiyou-data_01",
        "pool_policy": "default",
        "shard_begin": 0,
        "shard_end": 999
    }
}

# user = db.user.select_list(clazz=User, where="id = $id", vars={"id":id})
# user为配置的数据源名称,读取配置之后会自动把所有数据源名称作为db模块的属性,可以直接点号访问
# 如果user有从库有主库，那么会去根据读写操作来自动判断使用哪个库
# select_list方法可以从DB获取多行数据，并且自动将行映射成对象
# @param clazz: 对象类型
# @param where: 条件
# @param vars: 参数
# 其实就是简单对web.py的db访问层做下包装

# Shard:

# feed_index_list = db.user.select_list(clazz=FeedIndex, where="user_id=$user_id", vars={"user_id":user_id}, shard_id=10000)
# 需要额外指定一个shard_id参数，然后用这个参数去取模，然后去获得表名
