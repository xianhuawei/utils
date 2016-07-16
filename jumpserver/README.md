# jumpserver
    堡垒机 跳板机

# 原则
    简单 ,无agent ,无端口监听,操作机除了ssh 不开其它服务
    易组合,不做资产管理,通过restful接口组合其它系统

# 安装
    操作机:
        yum install -y python-pip MySQL-python ansible
        pip install pyte torndb
        cp jumpserver.py /usr/sbin/shell
        修改jumpserver.py中的接口和配置,例如是否记录到db,db配置,get_user_host_list_url 等
    
    中控机(接收参数跑ansible playbook,用来同步帐号&同步权限):
        yum install -y ansible python-gevent python-simplejson python-requests

#  运行
     中控机:
            nohup python web_task.py &

# 使用
    base 实现用户,产品,ip的列表接口 返回类似下面的json数据
        '''
        [
            {
                "business": "flymebbs", //业务
                "container": "nginx",   //容器
                "datacenter": "GZ-NS",  //机房
                "ip": "1.1.1.53",       // ip
                "model": "nginx",       //模块
                "remarks": null         //备注
            },
            {
                "business": "flymebbs",
                "container": "nginx",
                "datacenter": "GZ-NS",
                "ip": "1.1.1.54",
                "model": "nginx",
                "remarks": null
            },
            {
                "business": "flymebbs",
                "container": "nginx",
                "datacenter": "GZ-NS",
                "ip": "1.1.1.55",
                "model": "nginx",
                "remarks": ""
            },
            {
                "business": "flymebbs",
                "container": "nginx",
                "datacenter": "GZ-NS",
                "ip": "1.1.1.56",
                "model": "nginx",
                "remarks": null
            }
        ]
        '''
        需要这些字段是方便标识某台机器,当然 核心还是 ip必填 其它可为空

        然后修改jumpserver.py的
            get_user_host_list_url = 'http://example.com/v1/get_user_host_list_url'
        为刚才的restful api

        修改ansible的hosts文件 默认在 /etc/ansible/hosts 其中center_control为中控机ip jumpserver为操作机ip
              '''
                [center_control]
                1.1.1.1

                [jumpserver]
                3.3.3.3
                2.2.2.2
                4.4.4.4
             '''

        1,添加用户
           提交参数数据到center_control_ip
           例如
               curl -x POST -d '{"playbook":"./center_control.yml","extra_vars":{"action":"create_account_key","user_name":"zhangsan","uid":"333333"}}' http://center_control_ip:8080
       2,添加权限
           提交参数数据到center_control_ip
           例如
               curl -x POST -d '{"playbook":"./center_control.yml","extra_vars":{"action":"create_sudoers","user_name":"zhangsan","cmd_list":"/sbin/fdisk,/sbin/iptables"}}' http://center_control_ip:8080
       3,添加用户管理的机器
           提交参数数据到center_control_ip
           例如
               curl -x POST -d '{"hosts":"1.1.1.1,2.2.2.2,3.3.3.3","playbook":"./jumpserver.yml","extra_vars":{"action":"sync__authorized_keys","user_name":"zhangsan","uid":"333333"}}' http://center_control_ip:8080
       4,添加用户权限的机器
           提交参数数据到center_control_ip
           例如
               curl -x POST -d '{"hosts":"1.1.1.1,2.2.2.2,3.3.3.3","playbook":"./jumpserver.yml","extra_vars":{"action":"sync__authorized_keys","user_name":"zhangsan","uid":"333333"}}' http://center_control_ip:8080
       5,删除权限
           提交参数数据到center_control_ip
           例如
               curl -x POST -d '{"hosts":"1.1.1.1,2.2.2.2,3.3.3.3","playbook":"./jumpserver.yml","extra_vars":{"action":"del_sudoers","user_name":"zhangsan"}}' http://center_control_ip:8080
       6,删除用户
           提交参数数据到center_control_ip
           例如
               curl -x POST -d '{"hosts":"1.1.1.1,2.2.2.2,3.3.3.3","playbook":"./jumpserver.yml","extra_vars":{"action":"del_account_ip","user_name":"zhangsan"}}' http://center_control_ip:8080
    7,开启审计 监控 录像回放 统计等功能
        建表
             '''
                CREATE TABLE `alert` (
                  `id` int(11) NOT NULL AUTO_INCREMENT,
                  `msg` varchar(20) NOT NULL,
                  `time` datetime DEFAULT NULL,
                  `is_finished` bigint(20) NOT NULL,
                  PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

                CREATE TABLE `execlog` (
                  `id` int(11) NOT NULL AUTO_INCREMENT,
                  `user` varchar(100) NOT NULL,
                  `host` longtext NOT NULL,
                  `cmd` longtext NOT NULL,
                  `remote_ip` varchar(100) NOT NULL,
                  `result` longtext NOT NULL,
                  `datetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

                CREATE TABLE `filelog` (
                  `id` int(11) NOT NULL AUTO_INCREMENT,
                  `user` varchar(100) NOT NULL,
                  `host` longtext NOT NULL,
                  `filename` longtext NOT NULL,
                  `type` varchar(20) NOT NULL,
                  `remote_ip` varchar(100) NOT NULL,
                  `result` longtext NOT NULL,
                  `datetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                  PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

                CREATE TABLE `log` (
                  `id` int(11) NOT NULL AUTO_INCREMENT,
                  `user` varchar(20) DEFAULT NULL,
                  `host` varchar(200) DEFAULT NULL,
                  `remote_ip` varchar(100) NOT NULL,
                  `login_type` varchar(100) NOT NULL,
                  `log_path` varchar(100) NOT NULL,
                  `start_time` datetime DEFAULT NULL,
                  `pid` int(11) NOT NULL,
                  `is_finished` tinyint(1) NOT NULL DEFAULT '1',
                  `end_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
                  `filename` varchar(40) NOT NULL DEFAULT '',
                  PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

                CREATE TABLE `termlog` (
                  `id` int(11) NOT NULL AUTO_INCREMENT,
                  `logPath` longtext NOT NULL,
                  `filename` varchar(40) NOT NULL,
                  `logPWD` longtext NOT NULL,
                  `nick` longtext,
                  `log` longtext,
                  `history` longtext,
                  `log_id` varchar(100) DEFAULT NULL,
                  `timestamp` varchar(100) NOT NULL,
                  `datetimestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

                CREATE TABLE `termlog_user` (
                  `id` int(11) NOT NULL AUTO_INCREMENT,
                  `termlog_id` int(11) NOT NULL,
                  `user_id` int(11) NOT NULL,
                  PRIMARY KEY (`id`),
                  UNIQUE KEY `termlog_id` (`termlog_id`,`user_id`),
                  KEY `jlog_termlog_user_ac108316` (`termlog_id`),
                  KEY `jlog_termlog_user_6340c63c` (`user_id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

                CREATE TABLE `ttylog` (
                  `id` int(11) NOT NULL AUTO_INCREMENT,
                  `log_id` int(11) NOT NULL,
                  `datetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  `cmd` varchar(200) NOT NULL,
                  PRIMARY KEY (`id`),
                  KEY `jlog_ttylog_695186c0` (`log_id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
                '''
            修改 jumpserver的db配置
                db_config = {
                    'host': "1.1.1.1",
                    'database': 'db_test',
                    'user': 'test',
                    'password': 'test'
                }

            打开jumpserver.py的
                is_log2db = True
            记录操作入库

