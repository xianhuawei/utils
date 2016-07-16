#!/usr/bin/env python
# -*- coding:utf8 -*-

import os
import shutil
import subprocess
import sys
import inspect

import jinja2
def render(template_file,params):
    loader = jinja2.FileSystemLoader('templates_src')
    render_env = jinja2.Environment(loader=loader)
    template = render_env.get_template(template_file)

    try:
        output = template.render(**params)
    except jinja2.UndefinedError as e:
        raise Exception(e)

    return output

dirs = ['config','controllers','models','templates','static']

def gen(project_name, database_host, database_user,database,database_passwd='',table='',database_port=3306):
    #gen config
    with open('configs/db.py','wb+') as f:
        f.write("db={ 'host':"+database_host+
                ',port:'+database_port+
                ',user:'+database_user+
                ',password:'+database_passwd+
                ',database:'+database+
                "}")

    #gen model
    p = subprocess.Popen('python -m pwiz -e mysql -u%s -H%s -P%s -p%d %s -t %s >./models/%s.py'%
                     (database_user,database_host,database_passwd,database_port,database,table,database+table),
                     shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE)

    try:
        stdout,stderr = p.communicate()
    finally:
        subprocess._cleanup()
        p.stdout.close()
        p.stderr.close()
    rc = p.returncode
    
    if rc !=0 :
        print "gen model error %s" % stderr
        sys.exit(1)
    #gen template

    #gen controller

    #copy
    for item in dirs:
        shutil.copy(item, os.path.join(project_name, item))


if __name__ == '__main__':
    project_name = raw_input('Project Name:')
    database_host = raw_input('Database host: default 127.0.0.1 ') or '127.0.0.1'
    database_user = raw_input('Database user: default root') or 'root'
    database_passwd = raw_input('Database password: default empty') or ''
    database_port = raw_input('Database port: default 3306') or 3306
    database = raw_input('Database :')
    table = raw_input('table : default all')

    if len(project_name) == 0 or ' ' in project_name:
        print('Invalid Project Name.')


    print('')
    print('   Project Name: %s' % project_name)
    print('  Database host: %s' % database_host)
    print('  Database user: %s' % database_user)
    print('')

    sure = raw_input('Sure (Y/n)?')

    if sure == 'n' or database == '':
        sys.exit(1)

    if os.path.exists(project_name):
        print('Already Exists!')
        sys.exit(1)


    gen(project_name=project_name, database_host=database_host, database_user=database_user,
        database_passwd=database_passwd,database=database,table=table,database_port=database_port)
    print('Done.')





