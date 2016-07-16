#!/usr/bin/env python
import sys
import os
import time
import simplejson as json
import sqlite3
import subprocess

name = sys.argv[2]
ip = sys.argv[3]

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

db_dir = '/data/cmdb/'
db = '/data/cmdb/inventory'

if not os.path.isfile(db):
    os.makedirs(db_dir)


def create_table():
    try:
        sqlite_conn = sqlite3.connect(db)
        sqlite_cursor = sqlite_conn.cursor()
    except:
        print "DB not accessible"

    try:
        sql1 = '''
                CREATE TABLE `facts` (
                  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                  `last_update` timestamp NULL DEFAULT NULL,
                  `hostname` varchar(300) DEFAULT NULL,
                  `architecture` varchar(300) DEFAULT NULL,
                  `distribution` varchar(300) DEFAULT NULL,
                  `distribution_version` varchar(300) DEFAULT NULL,
                  `system` varchar(300) DEFAULT NULL,
                  `kernel` varchar(300) DEFAULT NULL,
                  `ipv4` varchar(300) DEFAULT NULL,
                  `ipv6` varchar(300) DEFAULT NULL,
                  `devices` text,
                  `domain` varchar(300) DEFAULT NULL,
                  `eth0` text,
                  `eth1` text,
                  `fqdn` varchar(300) DEFAULT NULL,
                  `machine` varchar(300) DEFAULT NULL,
                  `machine_id` varchar(300) DEFAULT NULL,
                  `mounts` text,
                  `nodename` varchar(300) DEFAULT NULL,
                  `processor` text,
                  `processor_cores` int(3) DEFAULT NULL,
                  `processor_count` int(3) DEFAULT NULL,
                  `processor_threads_per_core` varchar(300) DEFAULT NULL,
                  `processor_vcpus` int(3) DEFAULT NULL,
                  `product_name` varchar(300) DEFAULT NULL,
                  `product_serial` varchar(300) DEFAULT NULL,
                  `product_uuid` varchar(300) DEFAULT NULL UNIQUE,
                  `product_version` varchar(300) DEFAULT NULL,
                  `selinux` varchar(300) DEFAULT NULL,
                  `system_vendor` varchar(300) DEFAULT NULL,
                  `virtualization_role` varchar(300) DEFAULT NULL,
                  `virtualization_type` varchar(300) DEFAULT NULL,
                  `bios_date` varchar(300) DEFAULT NULL,
                  `bios_version` varchar(300) DEFAULT NULL
                )
        '''
        sqlite_cursor.execute(sql1)

        sqlite_conn.commit()

        sql2 = '''
                CREATE TABLE `inventory` (
                  `product_uuid` varchar(300) DEFAULT NULL UNIQUE,
                  `price` varchar(25) DEFAULT NULL,
                  `role` varchar(25) DEFAULT NULL,
                  `product` varchar(25) DEFAULT NULL,
                  `owner` varchar(25) DEFAULT NULL,
                  `datacenter` varchar(25) DEFAULT NULL,
                  `rack` varchar(25) DEFAULT NULL ,
                  `environment` varchar(25) DEFAULT NULL ,
                  `tier` varchar(25) DEFAULT NULL 
                )
        '''
        sqlite_cursor.execute(sql2)
        sqlite_conn.commit()
    except sqlite3.Error, e:
        print("Something went wrong: {}".format(e))


def fact_to_db():
    p = subprocess.Popen("ansible all -i %s, -m setup -s" % ip,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    facts = p.stdout.read()
    p.wait()

    idx = facts.find('=>')
    data = json.loads(facts[idx + 2:].strip())
    facts = data.get('ansible_facts', None)
    facts = {
        'last_update' : time.strftime(TIME_FORMAT, time.localtime()),
        'bios_date' : facts.get('ansible_bios_date', None),
        'bios_version' :  facts.get('ansible_bios_version', None),
        'hostname' :  facts.get('ansible_hostname', None),
        'architecture' :  facts.get('ansible_architecture', None),
        'distribution' :  facts.get('ansible_distribution', None),
        'distribution_version' :  facts.get('ansible_distribution_version', None),
        'system' :  facts.get('ansible_system', None),
        'kernel' :  facts.get('ansible_kernel', None),
        'ipv4' :  facts.get('ansible_default_ipv4', None),
        'ipv6' :  facts.get('ansible_default_ipv6', None),
        'devices' :  facts.get('ansible_devices', None),
        'domain' :  facts.get('ansible_domain', None),
        'eth0' :  facts.get('ansible_eth0', None),
        'eth1' :  facts.get('ansible_eth1', None),
        'fqdn' :  facts.get('ansible_fqdn', None),
        'machine ' :  facts.get('ansible_machine', None),
        'machine_id' :  facts.get('ansible_machine_id', None),
        'mounts' :  facts.get('ansible_mounts', None),
        'nodename' :  facts.get('ansible_nodename', None),
        'processor' :  facts.get('ansible_processor', None),
        'processor_cores' :  facts.get('ansible_processor_cores', None),
        'processor_count' :  facts.get('ansible_processor_count', None),
        'processor_threads_per_core' :  facts.get(
            'ansible_processor_threads_per_core', None),
        'processor_vcpus' :  facts.get('ansible_processor_vcpus', None),
        'product_nam' : facts.get('ansible_product_name', None),
        'product_serial' : facts.get('ansible_product_serial', None),
        'product_uuid' : facts.get('ansible_product_uuid', None),
        'product_version' :  facts.get('ansible_product_version', None),
        'selinux' : facts.get('ansible_selinux', None),
        'system_vendor' : facts.get('ansible_system_vendor', None),
        'virtualization_role' :  facts.get('ansible_virtualization_role', None),
        'virtualization_type' :  facts.get('ansible_virtualization_type', None)
    }

    try:
        sqlite_conn = sqlite3.connect(db)
        sqlite_cursor = sqlite_conn.cursor()
    except:
        print "DB not accessible"
        sys.exit(1)
    try:
        #placeholders = ', '.join(['%s']*len(facts)) ##����dict���ȷ����磺%s, %s ��ռλ��
        placeholders = ', '.join(['\'%s\'']* len(facts))
        insert_sql="INSERT OR IGNORE INTO facts (%s) VALUES (%s)" %(','.join(facts.keys()),placeholders)

        sqlite_cursor.execute(insert_sql,facts.values())

    except sqlite3.Error, e:
        print("Something went wrong: {}".format(e))
    sqlite_conn.commit()


if __name__ == '__main__':
    if not os.path.isfile(db):
        create_table()
    fact_to_db()
