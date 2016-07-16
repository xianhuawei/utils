CREATE DATABASE `cmdb` ;

USE `cmdb`;
                
DROP TABLE IF EXISTS `device`;

CREATE TABLE `device` (
  `assets_id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `price` varchar(25) DEFAULT NULL COMMENT '价格',
  `environment` varchar(25) DEFAULT NULL COMMENT '环境 dev,pro,test,staging',
  `tier` varchar(25) DEFAULT NULL COMMENT '属于哪个tier',
  `server_type` tinyint(4) NOT NULL DEFAULT '1' COMMENT '设备类型：1：服务器，2：交换机，3：路由器，4：防火墙, 5:虚拟子机',
  `fqdn` varchar(255) DEFAULT NULL COMMENT '主机名称',
  `rack_id` int(10) unsigned NOT NULL COMMENT '机架id',
  `seat` int(11) NOT NULL COMMENT '机位',
  `manufacturer_id` varchar(100) DEFAULT NULL COMMENT '厂商型号',
  `logic_area` tinyint(4) DEFAULT '0' COMMENT '逻辑区域 0:虚拟化,1:lvs(fullnat),2:数据库,3:管理网区,4:大数据,5:外网区',
  `device_height` int(11) NOT NULL DEFAULT '2' COMMENT '设备高度（U）',
  `device_status` int(11) NOT NULL DEFAULT '2' COMMENT '状态 1：运营中，2：待运营，3：开发中，4：待上线，5：故障中，6：回收中',
  `purchase_date` date NOT NULL COMMENT '购买日期',
  `on_time` date NOT NULL COMMENT '上架时间',
  `service_number` varchar(255) DEFAULT NULL COMMENT '服务号',
  `quick_service_number` varchar(255) DEFAULT NULL COMMENT '快速服务代码',
  `sn` varchar(255) DEFAULT NULL COMMENT '产品SN号',
  `iso_num` varchar(40) DEFAULT 'iso编号',
  `warranty_time` char(255) DEFAULT '36' COMMENT '保修时间(月)',
  `operator` varchar(100) NOT NULL DEFAULT '' COMMENT '维护人员',
  `uuid` varchar(255) DEFAULT NULL COMMENT 'UUID',
  `disk_info` text COMMENT '存储信息;硬盘空间信息',
  `remarks` varchar(1024) DEFAULT NULL COMMENT '备注',
  `create_timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `os` varchar(255) DEFAULT NULL COMMENT '操作系统名称',
  `kernel` varchar(255) DEFAULT NULL COMMENT '内核版本',
  `cpu` text COMMENT 'CPU信息',
  `memory` varchar(255) DEFAULT NULL COMMENT '内存信息',
  `bios_date` varchar(100) DEFAULT NULL COMMENT 'bios日期',
  `bios_version` varchar(100) DEFAULT NULL COMMENT 'bios版本',
  PRIMARY KEY (`assets_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `level_tag`;

CREATE TABLE `level_tag` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `meta_name` varchar(100) DEFAULT NULL COMMENT 'tag',
  `meta_type` enum('level','tag') DEFAULT NULL COMMENT '类型,level,tag',
  `create_timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

insert  into `level_tag`(`id`,`meta_name`,`meta_type`,`create_timestamp`) values (1,'cop','level','2016-01-12 10:32:43'),(2,'owt','level','2016-01-12 10:32:43'),(3,'loc','level','2016-01-12 10:32:43'),(4,'idc','level','2016-01-12 10:32:43'),(5,'pdl','level','2016-01-12 10:32:43'),(6,'sbs','level','2016-01-12 10:32:43'),(7,'srv','level','2016-01-12 10:32:43'),(8,'mod','level','2016-01-12 10:32:43'),(9,'grp','level','2016-01-12 10:32:43'),(10,'ptn','level','2016-01-12 10:32:43'),(11,'cln','level','2016-01-12 10:32:43'),(12,'fls','level','2016-01-12 10:32:43'),(13,'status','level','2016-01-12 10:32:43'),(14,'virt','level','2016-01-12 10:32:43');


DROP TABLE IF EXISTS `room`;

CREATE TABLE `room` (
  `room_id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `room_name` varchar(255) NOT NULL COMMENT '机房名称',
  `position` varchar(255) NOT NULL COMMENT '机房位置',
  `room_name_short` varchar(4) DEFAULT NULL COMMENT '机房名简写',
  `city_short` varchar(4) DEFAULT NULL COMMENT '城市名简写',
  `tel` varchar(4) DEFAULT NULL COMMENT '客服电话',
  `customer_service` varchar(4) DEFAULT NULL COMMENT '客服',
  `email` varchar(4) DEFAULT NULL COMMENT '客服email',
  PRIMARY KEY (`room_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `segment`;

CREATE TABLE `segment` (
  `segment_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `assets_id` varchar(100) NOT NULL COMMENT '关联网络设备id',
  `segment_ip` varchar(255) NOT NULL COMMENT 'IP',
  `ip_type` tinyint(4) NOT NULL COMMENT 'IP类型 1：内网，2：外网',
  `mask` varchar(255) NOT NULL COMMENT '子网掩码',
  `gateway` varchar(255) NOT NULL COMMENT '网关',
  `vlan_id` varchar(20) DEFAULT '1' COMMENT 'VLAN ID',
  `total` int(255) NOT NULL DEFAULT '0' COMMENT 'IP总数',
  `assigned` int(255) NOT NULL DEFAULT '0' COMMENT '已分配',
  `carriers` tinyint(4) DEFAULT '0' COMMENT '运营商 0:内网，1:电信，2：联通，3教育网，4：移动，5：其他',
  `remarks` varchar(255) DEFAULT NULL COMMENT 'remarks',
  `status` tinyint(4) NOT NULL DEFAULT '0' COMMENT '状态：0：不启用，1：启用',
  `logic_area` tinyint(4) DEFAULT '0' COMMENT '逻辑区域 0:虚拟化,1:lvs(fullnat),2:数据库,3:管理网区,4:大数据,5:外网区',
  PRIMARY KEY (`segment_id`),
  UNIQUE KEY `segment_ip_mask` (`segment_ip`,`mask`),
  KEY `ip_type` (`ip_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `ip`;

CREATE TABLE `ip` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `assets_id` varchar(255) NOT NULL COMMENT '资产id',
  `ip` varchar(255) NOT NULL COMMENT 'IP',
  `is_vip` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否是vip 0:否,1:是',
  `mask` varchar(255) NOT NULL COMMENT '子网掩码',
  `segment_ip` varchar(255) NOT NULL COMMENT '网段',
  `gateway` varchar(255) NOT NULL COMMENT '网关',
  `carriers` tinyint(4) NOT NULL DEFAULT '0' COMMENT '运营商 0:内网，1:电信，2：网通，3教育网，4：移动，5：其他',
  `status` tinyint(4) NOT NULL DEFAULT '1' COMMENT '状态：0：不启用，1：启用',
  PRIMARY KEY (`id`),
  UNIQUE KEY `assets_id_ip_type` (`assets_id`,`ip`,`is_vip`),
  KEY `assets` (`assets_id`),
  KEY `carriers` (`carriers`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `segment_ip_pool`;

CREATE TABLE `segment_ip_pool` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `segment_id` int(10) unsigned NOT NULL COMMENT '网段ID',
  `ip` varchar(100) NOT NULL COMMENT 'IP',
  `assigned` tinyint(4) NOT NULL DEFAULT '0' COMMENT '状态：0：未分配，1：已分配',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ip` (`ip`),
  KEY `segment_id` (`segment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `server_tag`;

CREATE TABLE `server_tag` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `level_id` int(10) unsigned DEFAULT NULL,
  `server_tag_id` int(10) unsigned DEFAULT NULL,
  `create_timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `assets_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `server_tag_user`;

CREATE TABLE `server_tag_user` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `server_tag_id` int(11) DEFAULT NULL COMMENT 'tag id',
  `uid` int(11) DEFAULT NULL COMMENT '用户id',
  `create_timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB

#todo
asset_nic_mac #管理网卡mac,其它4网卡mac

asset_bonding 

asset_bridge

manufacturer #厂商

room_frame #机柜

software #安装的软件

instance #实例

upstream #上下游信息

listen_port #监听的端口

