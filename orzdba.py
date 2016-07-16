#!/usr/bin/env python
# -*- coding:utf-8 -*-
#---------------------------------------------------------------------------
#   Filename:              orzdba.py
#   Desc:
#
#---------------------------------------------------------------------------
from __future__ import division
from __future__ import print_function

headline1 = ''
headline2 = ''
mysql_headline1 = ''
mysql_headline2 = ''
ncpu      = 0        #Number of processors
# Options Flag
optflag   = 0        #whether input opt
timeFlag  = 0        # -t   : print current time
interval  = 1        # -i   : time(second) interval
my_load   = 0        # -l   : print load info
my_cpu    = 0        # -c   : print cpu  info
my_swap   = 0        # -s   : print swap info
my_disk   = None     # -d   : print disk info
my_net    = None     # -n   : print net info
mysql  = 0           # -mysql: print mysql status
mysql_conn =''      # mysql conn info
com   = 0;          # -com : print mysql status
innodb_hit  = 0     # -hit : Print Innodb Hit%
innodb_rows = 0     # -innodb_rows : Print Innodb Rows Status
innodb_pages= 0     # -innodb_pages: Innodb Buffer Pool Pages Status
innodb_data = 0     # -innodb_data : Innodb Data Status
innodb_log  = 0     # -innodb_log  : Innodb Log Status
innodb_status=0     # -innodb_status: Show Engine Innodb Status
threads     = 0     # -T   : Print Threads Status
bytes       = 0     # -B   : Print Bytes Status
my_port   = '3306'  # default prot 3306
my_socket =None     # sockfile
dbrt = 0            # -rt
lock_file=''
tcprstat_logfile=''
tcprstat_dir='/tmp/'
orz_logfile=None
old_console=''
logfile_by_day=0    # one day one logfile
# Variables For :
#-----> Get SysInfo (from /proc/stat): CPU
sys_cpu1   = (0,0,0,0,0,0,0,0)
total_1    = 0
#
#<----- Get SysInfo (from /proc/stat): CPU
#-----> Get SysInfo (from /proc/vmstat): SWAP
swap1 ={'pswpin':0,'pswpout':0}
swap_not_first = 0
#<----- Get SysInfo (from /proc/vmstat): SWAP
#-----> Get SysInfo (from /proc/net/dev): NET
net1 ={'recv':0,'send':0}
net_not_first = 0
#<----- Get SysInfo (from /proc/net/dev): NET
#-----> Get SysInfo (from /proc/diskstats): IO
sys_io1   = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
io_not_first  = 0;                                   # no print first value
#ncpu = `grep processor /proc/cpuinfo | wc -l`;     #/* Number of processors */
# grep "HZ" -R /usr/include/*
# /usr/include/asm-x86_64/param.h:#define HZ 100
HZ = 100
#<----- Get SysInfo (from /proc/diskstats): IO

#-----> Get Mysql Status
mystat1={"Com_select":0,
        "Com_delete":0 ,
        "Com_update":0,
        "Com_insert":0,
        "Innodb_buffer_pool_read_requests":0,
        "Innodb_rows_inserted":0,
        "Innodb_rows_updated":0,
        "Innodb_rows_deleted":0,
        "Innodb_rows_read":0,
        "Threads_created":0,
        "Bytes_received":0,
        "Bytes_sent":0,
        "Innodb_buffer_pool_pages_flushed":0,
        "Innodb_data_read":0,
        "Innodb_data_reads":0,
        "Innodb_data_writes":0,
        "Innodb_data_written":0,
        "Innodb_os_log_fsyncs":0,
        "Innodb_os_log_written":0}
mysql_no_first = 0
#<----- Get Mysql Status
HAS_COLOR=1
count=None     #times
python_version=''


import sys
if sys.version_info<(2,7):
    sys.exit('error: Python 2.7 or later required')
import time,datetime
import os,operator
import subprocess
import socket,fcntl,struct
import getopt
import argparse,signal
import multiprocessing
import atexit
ATTRIBUTES = dict(
        list(zip([
            'bold',
            'dark',
            '',
            'underline',
            'blink',
            '',
            'reverse',
            'concealed'
            ],
            list(range(1, 9))
            ))
        )
del ATTRIBUTES['']
HIGHLIGHTS = dict(
        list(zip([
            'on_grey',
            'on_red',
            'on_green',
            'on_yellow',
            'on_blue',
            'on_magenta',
            'on_cyan',
            'on_white'
            ],
            list(range(40, 48))
            ))
        )

COLORS = dict(
        list(zip([
            'grey',
            'red',
            'green',
            'yellow',
            'blue',
            'magenta',
            'cyan',
            'white',
            ],
            list(range(30, 38))
            ))
        )

RESET = '\033[0m'

#---------------------------------------------------------------------------
# 18.
# Function:
# ChangeLog:
#---------------------------------------------------------------------------
def colored(text, color=None, on_color=None, attrs=None):
    """Colorize text.

    Available text colors:
        red, green, yellow, blue, magenta, cyan, white.

    Available text highlights:
        on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white.

    Available attributes:
        bold, dark, underline, blink, reverse, concealed.

    Example:
        colored('Hello, World!', 'red', 'on_grey', ['blue', 'blink'])
        colored('Hello, World!', 'green')
    """
    if HAS_COLOR:
        if os.getenv('ANSI_COLORS_DISABLED') is None:
            fmt_str = '\033[%dm%s'
            if color is not None:
                text = fmt_str % (COLORS[color], text)

        if on_color is not None:
            text = fmt_str % (HIGHLIGHTS[on_color], text)

        if attrs is not None:
            for attr in attrs:
                text = fmt_str % (ATTRIBUTES[attr], text)
        text += RESET
    return text
#---------------------------------------------------------------------------
# 1.
# Function:
# ChangeLog:
#---------------------------------------------------------------------------

def cprint(text, color=None, on_color=None, attrs=None, **kwargs):
    """Print colorize text.

    It accepts arguments of print function.
    """

    print((colored(text, color, on_color, attrs)), **kwargs)

#---------------------------------------------------------------------------
# 1.
# Function: get hostname
# ChangeLog:
#---------------------------------------------------------------------------
def hostname():
    sys = os.name
    if sys == 'nt':
       hostname = os.getenv('computername')
       return hostname
    elif sys == 'posix':
       hostname = socket.gethostname()
       return hostname
    else:
          return 'Unkwon hostname'
#---------------------------------------------------------------------------
# 2.
# Function:get ipaddress
# ChangeLog:
#---------------------------------------------------------------------------
def get_ip_address():

    localIP = socket.gethostbyname(socket.gethostname())
    return localIP
#---------------------------------------------------------------------------
# 3.
# Function: handle ctrl+C
# ChangeLog:
#---------------------------------------------------------------------------
def catch_zap(signalNun,   currentStackFrame):

#     cprint ("\nExit Now...\n\n",'red')
     sys.exit(0)
#---------------------------------------------------------------------------
# 4.
# Function: Clear logfile
# ChangeLog:
#---------------------------------------------------------------------------
@atexit.register
def ClearFile():
    if dbrt:
       if os.path.isfile(lock_file):
           try:
               os.remove(lock_file)
           except OSError:
                os.system("rm -f %s" % lock_file)
       if os.path.isfile(tcprstat_logfile):
           try:
               os.remove(tcprstat_logfile)
           except OSError:
               os.system("rm -f %s" % tcprstat_logfile)
    if orz_logfile is not None:
       sys.stdout.close
       sys.stdout=old_console
       HAS_COLOR=1
       cprint('--------write log end--------------------------','green',end='')
    cprint("\nExit Now...\n\n",'red')
#---------------------------------------------------------------------------
# 5.
# Function:
# ChangeLog:
#---------------------------------------------------------------------------
def get_options():
    #define args
    parser = argparse.ArgumentParser(description='orzdba tool')
    parser.add_argument('-i','--interval',action='store',help='Time(second) Interval.',type=int,default=1)
    parser.add_argument('-t','--time',action='store_true',help='Print The Current Time.')
    parser.add_argument('-sys',action='store_true',help='print SysInfo (include -l,-c,-s).')
    parser.add_argument('-l','--load',action='store_true',help='Print Load Info.')
    parser.add_argument('-c','--cpu',action='store_true',help='Print Cpu Info.')
    parser.add_argument('-d','--disk',action='store',help='Print Disk Info.')
    parser.add_argument('-n','--net',action='store',help='Print Net Info.Time.')
    parser.add_argument('-s','--swap',action='store_true',help='Print The Swap Info.')
    parser.add_argument('-com',action='store_true',help='print mysql status.')
    parser.add_argument('-innodb_rows',action='store_true',help='Print Innodb Rows Status.')
    parser.add_argument('-innodb_pages',action='store_true',help=' Print Innodb Buffer Pool Pages Status.')
    parser.add_argument('-innodb_data',action='store_true',help='Print Innodb Data Status.')
    parser.add_argument('-innodb_log',action='store_true',help='Print Innodb Log  Status.')
    parser.add_argument('-innodb_status',action='store_true',help='Print Innodb Status from Command: "Show Engine Innodb Status".')
    parser.add_argument('-innodb',action='store_true',help='Print Innodb Info.')
    parser.add_argument('-T','--threads',action='store_true',help='Print Threads Status.')
    parser.add_argument('-B','--bytes',action='store_true',help='Print Bytes Status.')
    parser.add_argument('-rt',action='store_true',help='Print MySQL DB RT.')
    parser.add_argument('-hit',action='store_true',help='Print Innodb Hit%%')
    parser.add_argument('-mysql',action='store_true',help='print SysInfo (Print MySQLInfo (include -t,-com,-hit,-T,-B).')
    parser.add_argument('-P','--port',action='store',help='Port number to use for mysql connection(default 3306).')
    parser.add_argument('-S','--socket',action='store',help='Socket file to use for mysql connection.')
    parser.add_argument('-C','--count',action='store', help='Times.',type=int)
    parser.add_argument('-L','--logfile',action='store',help='ath of logfile.')
    parser.add_argument('-logfile_by_day',action='store_true',help='one day a logfile.')
    parser.add_argument('-lazy',action='store_true',help='Print Info (include -t,-l,-c,-s,-m,-hit).')
    parser.add_argument('--nocolor',action='store_true',help='Print NO color.')

    #parser.print_help()
    opts = parser.parse_args()
    #parser.print_usage()
    if opts.lazy:
       opts.time=opts.load=opts.cpu=opts.swap=opts.com=mysql=1

    if (opts.threads or opts.bytes or opts.rt or opts.com or opts.hit or opts.innodb_rows or opts.innodb_pages or opts.innodb_data or opts.innodb_log or opts.innodb_status):mysql=1

    if opts.sys:
       opts.time=opts.load=opts.cpu=opts.swap=opts.time=1

    if opts.innodb:
       opts.time=opts.innodb_pages =opts.innodb_data =opts.innodb_log =opts.innodb_status =mysql = 1

    if opts.mysql:
       mysql=opts.time=opts.com=opts.hit=opts.threads=opts.bytes=1
    if opts.nocolor or opts.logfile is not None:
        HAS_COLOR=0
    else:
        HAS_COLOR=1
    if opts.logfile is not None:
        orz_logfile=opts.logfile
        if opts.logfile_by_day:
            logfile_by_day=opts.logfile_by_day

    # set Headline
    if opts.time:
       headline1 = colored('--------','blue',attrs=['bold'])
       headline2 = colored('  time  |','blue',attrs=['bold','underline'])
       timeFlag = 1
       optflag  = 1
    if opts.load:
       headline1 +=colored(' -----load-avg----','blue',attrs=['bold'])
       headline2 +=colored('  1m    5m   15m |','blue',attrs=['bold','underline'])
       my_load = 1
       optflag = 1
    if opts.cpu:
       headline1 +=colored(' ---cpu-usage--- ','blue',attrs=['bold'])
       headline2 +=colored('usr sys idl iow|','blue',attrs=['bold','underline'])
       my_cpu = 1
       optflag = 1
    if opts.swap:
       headline1 += colored('---swap--- ','blue',attrs=['bold'])
       headline2 += colored('   si   so|','blue',attrs=['bold','underline'])
       my_swap = 1
       optflag = 1
    if opts.net:
       headline1 += colored(' -----net(B)----- ','blue',attrs=['bold'])
       headline2 += colored('    recv   send |','blue',attrs=['bold','underline'])
       optsflag = 1
    if opts.disk:
       headline1 += colored('-------------------------io-usage----------------------- ','blue',attrs=['bold'])
       headline2 += colored('   r/s    w/s    rkB/s    wkB/s  queue await svctm \%util|','blue',attrs=['bold','underline'])
       optsflag =1

    if opts.com:
       mysql_headline1 += colored('-----------QPS--TPS----------- ','green','on_blue',attrs=['bold'])
       mysql_headline2 += colored('  ins   upd   del    sel   iud|','green',attrs=['bold','underline'])
       com=optflag=1
    if opts.hit:
       mysql_headline1 +=colored('------Hit%----- ','green','on_blue',attrs=['bold'])
       mysql_headline2 +=colored('    lor     hit|','green',attrs=['bold','underline'])
       innodb_hit=optflag=1
    if opts.innodb_rows:
       mysql_headline1 +=colored('---innodb rows status--- ','green','on_blue',attrs=['bold'])
       mysql_headline2 +=colored('  ins   upd   del   read|','green',attrs=['bold','underline'])
       innodb_rows=optflag=1
    if opts.innodb_pages:
       mysql_headline1 +=colored('---innodb bp pages status-- ','green','on_blue',attrs=['bold'])
       mysql_headline2 += colored('   data   free  dirty flush|','green',attrs=['bold','underline'])
       innodb_pages=optflag=1
    if opts.innodb_data:
       mysql_headline1 += colored('-----innodb data status---- ','green','on_blue',attrs=['bold'])
       mysql_headline2 += colored(' reads writes  read written|','green',attrs=['bold','underline'])
       innodb_data=optflag=1
    if opts.innodb_log:
       mysql_headline1 +=colored('--innodb log-- ','green','on_blue',attrs=['bold'])
       mysql_headline2 += colored('fsyncs written|','green',attrs=['bold','underline'])
       innodb_log=optflag=1
    if opts.innodb_status:
       mysql_headline1 +=colored('  his --log(byte)--  read ---query--- ','green','on_blue',attrs=['bold'])
       mysql_headline2 +=colored(' list uflush  uckpt  view inside  que|','green',attrs=['bold','underline'])
       innodb_status=optflag=1
    if opts.threads:
       mysql_headline1 +=colored('------threads------ ','green','on_blue',attrs=['bold'])
       mysql_headline2 +=colored(' run  con  cre  cac|','green',attrs=['bold','underline'])
       threads=optflag=1
    if opts.bytes:
       mysql_headline1 +=colored('-----bytes---- ','green','on_blue',attrs=['bold'])
       mysql_headline2 +=colored('   recv   send|','green',attrs=['bold','underline'])
       bytes=optflag=1
    if opts.rt:
       mysql_headline1 +=colored('--------tcprstat(us)-------- ','green','on_blue',attrs=['bold'])
       mysql_headline2 +=colored('  count    avg 95-avg 99-avg|','green',attrs=['bold','underline'])
       dbrt=optflag=1
    if opts.port is not None:my_port=opts.port
    if opts.socket is not None:my_socket=opts.socket
    if opts.net is not None:my_net=opts.net
    if opts.disk is not None:my_disk=opts.disk
    if opts.count is not None:count=opts.count
    interval=opts.interval
    if optflag==0:
        parser.print_help()
    return opts
#---------------------------------------------------------------------------
# 6.
# Function:
# ChangeLog:
#---------------------------------------------------------------------------
def Print_title():

    cprint ("\n")
    cprint('.=================================================.','green')
    cprint('|       Welcome to use the orzdba tool !          |','green')
    cprint(colored("'=============== Date: ",'green')+colored(time.strftime("%Y-%m-%d", time.localtime()),'red')+colored(" ================'"+"\n",'green'))
    cprint(colored('HOST: ','red')+colored(hostname(),'yellow')+colored(" IP: ",'red')+colored(get_ip_address(),'yellow'))


    # Get MYSQL DB Name and Variables
    if mysql:
       (dbname,vars1,vars2) = get_mysql_vars()
       cprint(colored('DB  : ','red')+colored(dbname,'yellow'))
       cprint(colored('Var : ','red'),end='')
       i=0
       for var in vars1:
           #cprint(vars1)
           x=var.rstrip()
           #cprint(x.split('\t'))
           (vname,vvalue)=x.split("\t")

           if i%3==0 and i!=0:
               cprint(colored('      '+vname,'magenta')+colored('[','white'),end='')
           else:
               cprint(colored(vname,'magenta')+colored('[','white'),end='')

           if  operator.eq(vname,'max_binlog_cache_size') or operator.eq(vname,'max_binlog_size'):

               if float(vvalue)/1024/1024/1024>=1:
                   cprint ("{:.0f}".format(int(vvalue)/1024/1024/1024),'white',end='')
                   cprint ('G]','white',end='')
               else:
                   if float(vvalue)/1024/1024>=1:
                      cprint ("{:.0f}".format(int(vvalue)/1024/1024),'white',end='')
                      cprint ('M]','white',end='')
                   else:
                       cprint(colored(vvalue+']','white'),end='')

           else:
               cprint(colored(vvalue+']','white'),end='')
           i+=1
           if i%3==0:cprint('')
       cprint ('\n')
       i=0
       for var in vars2:
           x=var.rstrip()
           (vname,vvalue)=x.split("\t")

           if i%3==0:
               cprint(colored('      '+vname,'magenta')+colored('[','white'),end='')
           else:
               cprint(colored(vname,'magenta')+colored('[','white'),end='')

           if  operator.eq(vname,'innodb_log_file_size') or operator.eq(vname,'innodb_log_buffer_size') or operator.eq(vname,'innodb_buffer_pool_size'):

               if float(vvalue)/1024/1024/1024>=1:
                   cprint ("{:.0f}".format(int(vvalue)/1024/1024/1024),'white',end='')
                   cprint ('G]','white',end='')
               else:
                   if float(vvalue)/1024/1024>=1:
                      cprint ("{:.0f}".format(int(vvalue)/1024/1024),'white',end='')
                      cprint ('M]','white',end='')
                   else:
                       cprint(colored(vvalue+']','white'),end='')

           else:
               cprint(colored(vvalue+']','white'),end='')
           i+=1
           if i%3==0:cprint('')
       cprint ('\n')
#---------------------------------------------------------------------------
# 7.
# Function:
# ChangeLog:
#---------------------------------------------------------------------------
def get_mysql_vars():
   #get dbname
   p=subprocess.Popen(mysql_conn+' -e "show databases" |grep -iwvE "information_schema|mysql|test" | tr "\n" "|"',shell=True,stdout=subprocess.PIPE)
   out=p.communicate()[0]
   if python_version.major==3:
      dbname=str(out,encoding='utf8').rstrip('|')
   elif python_version.major==2:
      dbname=out.rstrip('|')
   #get variables
   s1='show variables where Variable_name in ("sync_binlog","max_connections","max_user_connections","max_connect_errors","table_open_cache","table_definition_cache","thread_cache_size","binlog_format","open_files_limit","max_binlog_size","max_binlog_cache_size")'
   p=subprocess.Popen(mysql_conn+"  -e '"+s1+"'",shell=True,stdout=subprocess.PIPE)
   out=p.communicate()[0].rstrip()
   #cprint(str(python_version.major))
   if python_version.major==2:
      vars1=out.split('\n')
   elif python_version.major==3:
      vars1=str(out,encoding='utf8').split('\n')
   s1='show variables where Variable_name in ("innodb_flush_log_at_trx_commit","innodb_flush_method","innodb_buffer_pool_size","innodb_max_dirty_pages_pct","innodb_log_buffer_size","innodb_log_file_size","innodb_log_files_in_group","innodb_thread_concurrency","innodb_file_per_table","innodb_adaptive_hash_index","innodb_open_files","innodb_io_capacity","innodb_read_io_threads","innodb_write_io_threads","innodb_adaptive_flushing","innodb_lock_wait_timeout","innodb_log_files_in_group")'
   p=subprocess.Popen(mysql_conn+"  -e '"+s1+"'",shell=True,stdout=subprocess.PIPE)
   out=p.communicate()[0].rstrip()
   if python_version.major==2:
       vars2=out.split('\n')
   elif python_version.major==3:
       vars2=str(out,encoding='utf8').split('\n')
   #print vars2
   return(dbname,vars1,vars2)
#---------------------------------------------------------------------------
# 8.
# Function:
# ChangeLog:
#---------------------------------------------------------------------------
def load_stat():
    loadavg = {}
    f = open("/proc/loadavg")
    con = f.read().split()
    f.close()
    loadavg['lavg_1']=con[0]
    loadavg['lavg_5']=con[1]
    loadavg['lavg_15']=con[2]
    loadavg['nr']=con[3]
    loadavg['last_pid']=con[4]
    return loadavg
#---------------------------------------------------------------------------
# 9.
# Function:
# ChangeLog:
#---------------------------------------------------------------------------
def  readCpuInfo():

    #line format :(http://blog.csdn.net/nineday/archive/2007/12/11/1928847.aspx)
    #cpu   1-user  2-nice  3-system 4-idle   5-iowait  6-irq   7-softirq
    cpuinfo={}
    f = open('/proc/stat')
    lines = f.readlines();
    f.close()

    for line in lines:
        line = line.lstrip()
        sys_cpu2 = line.split()
        if len(sys_cpu2) < 5:
            continue
        if sys_cpu2[0].startswith('cpu'):
            break

    total_2 = 0
    for i in range(1, len(sys_cpu2)):
        total_2= total_2 + int(sys_cpu2[i])

    user_diff   = int(sys_cpu2[1]) + int(sys_cpu2[2]) - int(sys_cpu1[1]) - int(sys_cpu1[2])
    system_diff = int(sys_cpu2[3]) + int(sys_cpu2[6]) + int(sys_cpu2[7]) - int(sys_cpu1[3]) - int(sys_cpu1[6]) - int(sys_cpu1[7])
    idle_diff   = int(sys_cpu2[4]) - int(sys_cpu1[4])
    iowait_diff = int(sys_cpu2[5]) - int(sys_cpu1[5])
    total_diff  =total_2-total_1
    user_diff_1   = int((user_diff/total_diff)*100 + 0.5 )
    system_diff_1 = int((system_diff/total_diff)*100 + 0.5 )
    idle_diff_1   = int((idle_diff/total_diff)*100 + 0.5 )
    iowait_diff_1 = int((iowait_diff/total_diff)*100 + 0.5 )
    cpuinfo['userdiff_t']  = user_diff_1
    cpuinfo['systemdiff_t']= system_diff_1
    cpuinfo['idlediff_t']  = idle_diff_1
    cpuinfo['iowaitdiff_t']= iowait_diff_1
    cpuinfo['userdiff']=user_diff
    cpuinfo['systemdiff']=system_diff
    cpuinfo['idlediff']=idle_diff
    cpuinfo['iowaitdiff']=iowait_diff
    sys_cpu1=sys_cpu2
    total_1=total_2
    return cpuinfo
#---------------------------------------------------------------------------
# 10.
# Function:
# ChangeLog:
#---------------------------------------------------------------------------
def get_swap():
    #Get SysInfo (from /proc/vmstat): SWAP
    #Detail Info : http://www.linuxinsight.com/proc_vmstat.html
    #pswpin/s：每秒系统换入的交换页面（swap page）数量
    #pswpout/s：每秒系统换出的交换页面（swap page）数量
    swap2={'pswpin':0,'pswpout':0}
    pswapinfo={}
    p=subprocess.Popen('cat /proc/vmstat |grep -E "pswpin|pswpout"',shell=True,stdout=subprocess.PIPE,bufsize=0)
    out=p.communicate()
    lines =out[0]
    if lines:
       x=lines.replace(b'\n',b' ')
       x=x.split()
       swap2['pswpin']=x[1]
       swap2['pswpout']=x[3]
    if swap_not_first:
        pswpindiff=int(swap2['pswpin'])-int(swap1['pswpin'])
        pswpoutdiff=int(swap2['pswpout'])-int(swap1['pswpout'])
    else:
        pswpindiff=0
        pswpoutdiff=0
    pswapinfo['pswpin']=pswpindiff
    pswapinfo['pswpout']=pswpoutdiff
    swap1=swap2
    swap_not_first +=1
    return pswapinfo
#---------------------------------------------------------------------------
# 11.
# Function:
# ChangeLog:
#---------------------------------------------------------------------------
def readNetInfo(dev):
    net2={}
    netdiff={}
    fd = open("/proc/net/dev", "r")
    for line in fd.readlines():
        if line.find(dev) > 0:
           field = line.split()
           net2['recv']=field[1]
           net2['send'] = field[9]
    fd.close()
    #p=subprocess.Popen('cat /proc/net/dev |grep "\\b'+dev+'\\b"',shell=True,stdout=subprocess.PIPE)
    #while p.poll()==None:
    #      lines = p.stdout.readlines()
    #for line in lines:
    #    line=line.replace(':',' ')
    #    items=line.split()
    #    net2['recv']=items[1]
    #    net2['send']=items[9]
    if net2:
       if net_not_first:
           recv_diff=(float(net2['recv'])-float(net1['recv']))/interval
           send_diff=(float(net2['send'])-float(net1['send']))/interval
       else:
            recv_diff=0
            send_diff=0
       netdiff['recv']=recv_diff
       netdiff['send']=send_diff
       net1=net2
       net_not_first +=1
    else:
        netdiff=None
    return netdiff
#---------------------------------------------------------------------------
# 12.
# Function:
# ChangeLog:
#---------------------------------------------------------------------------
def readDiskInfo(dev,deltams):
# Detail IO Info :
# (1) http://www.mjmwired.net/kernel/Documentation/iostats.txt
# (2) http://www.linuxinsight.com/iostat_utility.html
# (3) source code --> http://www.linuxinsight.com/files/iostat-2.2.tar.gz
# iostat --> line format :
# 0               1        2        3     4      5        6     7        8          9      10     11
# Device:       rrqm/s   wrqm/s   r/s   w/s    rkB/s    wkB/s avgrq-sz avgqu-sz   await  svctm  %util
# sda            0.05    12.44  0.42  7.60     5.67    80.15    21.42     0.04    4.63   0.55   0.44

    sys_io2=None
    sys_iodiff={}
    p=subprocess.Popen('cat /proc/diskstats |grep "\\b'+dev+'\\b"',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0)
    out = p.communicate()[0]
    sys_io2=out.split()
    #print len(sys_io2)
    if sys_io2 is None or len(sys_io2)==0:
       return None
    rd_ios     = float(sys_io2[3])  - float(sys_io1[3])   #/* Read I/O operations */
    rd_merges  = float(sys_io2[4])  - float(sys_io1[4])   #/* Reads merged */
    rd_sectors = float(sys_io2[5])  - float(sys_io1[5])   #/* Sectors read */
    rd_ticks   = float(sys_io2[6])  - float(sys_io1[6])   #/* Time in queue + service for read */
    wr_ios     = float(sys_io2[7])  - float(sys_io1[7])   #/* Write I/O operations */
    wr_merges  = float(sys_io2[8])  - float(sys_io1[8])   #/* Writes merged */
    wr_sectors = float(sys_io2[9])  - float(sys_io1[9])   #/* Sectors written */
    wr_ticks   = float(sys_io2[10]) - float(sys_io1[10])  #/* Time in queue + service for write */
    ticks      = float(sys_io2[12]) - float(sys_io1[12])  #/* Time of requests in queue */
    aveq       = float(sys_io2[13]) - float(sys_io1[13])  #/* Average queue length */

    n_ios      = 0        #/* Number of requests */
    n_ticks    = 0        #/* Total service time */
    n_kbytes   = 0        #/* Total kbytes transferred */
    busy       = 0        #/* Utilization at disk       (percent) */
    svc_t      = 0        #/* Average disk service time */
    wait       = 0        #/* Average wait */
    size       = 0        #/* Average request size */
    queue      = 0        #/* Average queue */

    n_ios    = rd_ios + wr_ios;
    n_ticks  = rd_ticks + wr_ticks
    n_kbytes = ( rd_sectors + wr_sectors) / 2.0
    queue    = aveq/deltams
    if n_ios==0:
        size=0
        wait=0
        svc_t=0
    else:
        size=n_kbytes / n_ios
        wait=n_ticks/ n_ios
        svc_t=ticks/n_ios

    busy = 100.0 * ticks / deltams;  #/* percentage! */
    if busy > 100:busy=100                                                                                                                                                                                                                           #
    rkbs     = (1000.0 * rd_sectors/deltams /2)
    wkbs     = (1000.0 * wr_sectors/deltams /2)
    # r/s  w/s
    rd_ios_s = (1000.0 * rd_ios/deltams)
    wr_ios_s = (1000.0 * wr_ios/deltams)
    #$rkbs,$wkbs,$queue,$wait,$svc_t,$busy
    sys_iodiff['rkbs']=rkbs
    sys_iodiff['wkbs']=wkbs
    sys_iodiff['queue']=queue
    sys_iodiff['wait']=wait
    sys_iodiff['svc_t']=svc_t
    sys_iodiff['busy']=busy
    sys_iodiff['rd_ios_s']=rd_ios_s
    sys_iodiff['wr_ios_s']=wr_ios_s
    sys_io1=sys_io2
    return sys_iodiff
#---------------------------------------------------------------------------
# 13.
# Function: Get Innodb Status from Command: 'Show Engine Innodb Status'
# ChangeLog:
#---------------------------------------------------------------------------
def get_innodb_status():

    innodb_status={}
    s1='show engine innodb status'
    p=subprocess.Popen(mysql_conn+"  -e '"+s1+"'",shell=True,stdout=subprocess.PIPE)
    out = p.communicate()[0].rstrip()
    vars=out.split('\\n')
    #print vars
    # http://code.goo.com/p/mysql-cacti-templates/source/browse/trunk/scripts/ss_get_mysql_stats.php
    #print len(vars)
    for var in vars:
        if var.find('History list length')>-1:
           items=var.split()
           innodb_status['history_list']=items[3]
        elif var.find('Log sequence number')>-1:
           items=var.split()
           innodb_status['log_bytes_written']=items[3]
        elif var.find('Log flushed up to')>-1:
           items=var.split()
           innodb_status['log_bytes_flushed']=items[4]
        elif var.find('Last checkpoint at')>-1:
           items=var.split()
           innodb_status['last_checkpoint']=items[3]
        elif var.find('queries inside InnoDB')>-1:
           items=var.split()
           innodb_status['queries_inside']=items[0]
           innodb_status['queries_queued']=items[4]
        elif var.find('read views open inside InnoDB')>-1:
           items=var.split()
           innodb_status['read_views']=items[0]
        #elif var.find('')>-1:
        #    items=var.split()
        #    print items
        #    innodb_status['']=items[3]
    innodb_status['unflushed_log'] = int(innodb_status['log_bytes_written']) - int(innodb_status['log_bytes_flushed'])
    innodb_status['uncheckpointed_bytes']=int(innodb_status['log_bytes_written']) - int(innodb_status['last_checkpoint'])
    return innodb_status
#---------------------------------------------------------------------------
# 14.
# Function:
# ChangeLog:
#---------------------------------------------------------------------------
def get_mysqlstat():

    mystat2={}
    if mysql:
       s1='show bal status where Variable_name in ("Com_select","Com_insert","Com_update","Com_delete","Innodb_buffer_pool_read_requests","Innodb_buffer_pool_reads","Innodb_rows_inserted","Innodb_rows_updated","Innodb_rows_deleted","Innodb_rows_read","Threads_running","Threads_connected","Threads_cached","Threads_created","Bytes_received","Bytes_sent","Innodb_buffer_pool_pages_data","Innodb_buffer_pool_pages_free","Innodb_buffer_pool_pages_dirty","Innodb_buffer_pool_pages_flushed","Innodb_data_reads","Innodb_data_writes","Innodb_data_read","Innodb_data_written","Innodb_os_log_fsyncs","Innodb_os_log_written")'
       p=subprocess.Popen(mysql_conn+"  -e '"+s1+"'",shell=True,stdout=subprocess.PIPE)
       out = p.communicate()[0].rstrip()
       #print out
       if python_version.major==2:
           vars=out.split('\n')
           for var in vars:
               (vname,vvalue)=var.split('\t')
               mystat2[vname]=vvalue
       elif python_version.major==3:
           vars=str(out,encoding='utf8').split('\n')
           for var in vars:
               (vname,vvalue)=var.split('\t')
               mystat2[vname]=vvalue
       #print mysql_no_first
       if mysql_no_first:
          insert_diff =(int(mystat2["Com_insert"]) - int(mystat1["Com_insert"]))/interval
          update_diff =(int(mystat2["Com_update"]) - int(mystat1["Com_update"]))/interval
          delete_diff =(int(mystat2["Com_delete"]) - int(mystat1["Com_delete"]))/interval
          select_diff =(int(mystat2["Com_select"]) - int(mystat1["Com_select"]))/interval
          read_request =(int(mystat2["Innodb_buffer_pool_read_requests"]) - int(mystat1["Innodb_buffer_pool_read_requests"]))/interval
          read         =(int(mystat2["Innodb_buffer_pool_reads"]) - int(mystat1["Innodb_buffer_pool_reads"]))/interval
          innodb_rows_inserted_diff =(int(mystat2["Innodb_rows_inserted"]) - int(mystat1["Innodb_rows_inserted"]))/interval
          innodb_rows_updated_diff  =(int(mystat2["Innodb_rows_updated"])  - int(mystat1["Innodb_rows_updated"]))/interval
          innodb_rows_deleted_diff  =(int(mystat2["Innodb_rows_deleted"])  - int(mystat1["Innodb_rows_deleted"]))/interval
          innodb_rows_read_diff     = (int(mystat2["Innodb_rows_read"])    - int(mystat1["Innodb_rows_read"]))/interval
          innodb_bp_pages_flushed_diff=(int(mystat2["Innodb_buffer_pool_pages_flushed"]) - int(mystat1["Innodb_buffer_pool_pages_flushed"]))/interval
          innodb_data_reads_diff    = (int(mystat2["Innodb_data_reads"])    - int(mystat1["Innodb_data_reads"])     ) /interval
          innodb_data_writes_diff   = (int(mystat2["Innodb_data_writes"])   - int(mystat1["Innodb_data_writes"])    ) /interval
          innodb_data_read_diff     = (int(mystat2["Innodb_data_read"])     - int(mystat1["Innodb_data_read"])      ) /interval
          innodb_data_written_diff  = (int(mystat2["Innodb_data_written"])  - int(mystat1["Innodb_data_written"])   ) /interval
          innodb_os_log_fsyncs_diff = (int(mystat2["Innodb_os_log_fsyncs"]) - int(mystat1["Innodb_os_log_fsyncs"])  ) /interval
          innodb_os_log_written_diff= (int(mystat2["Innodb_os_log_written"])- int(mystat1["Innodb_os_log_written"]) ) /interval
          threads_created_diff      = (int(mystat2["Threads_created"])      - int(mystat1["Threads_created"])      ) /interval
          bytes_received_diff       = (int(mystat2["Bytes_received"])       - int(mystat1["Bytes_received"])       ) /interval
          bytes_sent_diff           = (int(mystat2["Bytes_sent"])          - int(mystat1["Bytes_sent"])           ) /interval
          if com:
             # Com_insert # Com_update # Com_delete
             cprint ("{:>5.0f}{:6.0f}{:>6.0f}".format(insert_diff,update_diff,delete_diff),'white',end='')
             # Com_select
             cprint("{:7.0f}".format(select_diff),'yellow',end='')
             # Total TPS
             cprint("{:>6.0f}".format(insert_diff+update_diff+delete_diff),'yellow',end='')
             cprint('|','green',attrs=['bold'],end='')
          if innodb_hit:
             # Innodb_buffer_pool_read_requests
             cprint("{:>7.0f}".format(read_request),'white',end='')
             # Hit% : (Innodb_buffer_pool_read_requests - Innodb_buffer_pool_reads) / Innodb_buffer_pool_read_requests * 100%
             if read_request>0:
                hit =(read_request-read)/read_request*100
                if hit>99:
                    cprint("{:>8.2f}".format(hit),'green',end='')
                else:
                    cprint ("{:>8.2f}".format(hit),'red',end='')
             else:
                 cprint("{:>8.2f}".format(100.00),'green',end='')
             cprint('|','green',attrs=['bold'],end='')
          if innodb_rows:
             #Innodb_rows_inserted,Innodb_rows_updated,Innodb_rows_deleted,Innodb_rows_read
             cprint("{:>5.0f}{:>6.0f}{:>6.0f}{:>7.0f}".format(innodb_rows_inserted_diff,innodb_rows_updated_diff,innodb_rows_deleted_diff,innodb_rows_read_diff),'white',end='')
             cprint('|','green',attrs=['bold'],end='')
          if innodb_pages:
             # Innodb_buffer_pool_pages_data/free/dirty/flushed
             cprint("{:>7.0f}{:>7.0f}".format(int(mystat2["Innodb_buffer_pool_pages_data"]),int(mystat2["Innodb_buffer_pool_pages_free"])),'white',end='')
             cprint("{:>7.0f}{:>6.0f}".format(int(mystat2["Innodb_buffer_pool_pages_dirty"]),innodb_bp_pages_flushed_diff),'yellow',end='')
             cprint('|','green',attrs=['bold'],end='')
          if innodb_data:
             # Innodb_data_reads/writes/read/written
              cprint("{:>6.0f}{:>7.0f}".format(innodb_data_reads_diff,innodb_data_writes_diff),'white',end='')
              if innodb_data_read_diff/1024/1024>1:
                 if innodb_data_read_diff/1024/1024>9:
                     cprint("{:>6.1f}".format(innodb_data_read_diff/1024/1024)+'m','red',end='')
                 else:
                     cprint("{:>6.1f}".format(innodb_data_read_diff/1024/1024)+'m','white',end='')
              elif innodb_data_read_diff/1024>1:
                  cprint("{:>6.0f}".format(innodb_data_read_diff/1024)+'k','white',end='')
              else:
                  cprint("{:>6.0f}".format(innodb_data_read_diff),'white',end='')
              if innodb_data_written_diff/1024/1024>1:
                 if innodb_data_written_diff/1024/1024>9:
                    cprint("{:>8.1f}".format(innodb_data_written_diff/1024/1024)+'m','red',end='')
                 else:
                    cprint("{:>8.1f}".format(innodb_data_written_diff/1024/1024)+'m','white',end='')
              elif innodb_data_written_diff/1024>1:
                    cprint("{:>8.0f}".format(innodb_data_written_diff/1024)+'k','white',end='')
              else:
                    cprint("{:>8.0f}".format(innodb_data_read_diff),'white',end='')
              cprint('|','green',attrs=['bold'],end='')
          if innodb_log:
             # Innodb_os_log_fsyncs/written
              cprint("{:>6.0f}".format(innodb_os_log_fsyncs_diff),'white',end='')
              if innodb_os_log_written_diff/1024/1024>1:
                 cprint("{:>8.1f}".format(innodb_os_log_written_diff/1024/1024)+'m','red',end='')
              elif innodb_os_log_written_diff/1024>1:
                   cprint("{:>8.0f}".format(innodb_os_log_written_diff/1024)+'k','yellow',end='')
              else:
                   cprint("{:>8.0f}".format(innodb_os_log_written_diff),'yellow',end='')
              cprint('|','green',attrs=['bold'],end='')
          if innodb_status:
             innodb_status=get_innodb_status()
             cprint("{:>5.0f}".format(int(innodb_status['history_list'])),'white',end='')
             if int(innodb_status['unflushed_log'])/1024/1024>1:
                cprint("{:>6.1f}".format(int(innodb_status['unflushed_log'])/1024/1024)+'m','yellow',end='')
             elif int(innodb_status['unflushed_log'])/1024>1:
                cprint("{:>6.1f}".format(int(innodb_status['unflushed_log'])/1024)+'k','yellow',end='')
             else:
                cprint("{:>6.1f}".format(int(innodb_status['unflushed_log']))+'b','yellow',end='')
             if int(innodb_status['uncheckpointed_bytes'])/1024/1024>1:
                cprint("{:>6.1f}".format(int(innodb_status['uncheckpointed_bytes'])/1024/1024)+'m','yellow',end='')
             elif int(innodb_status['uncheckpointed_bytes'])/1024>1:
                cprint("{:>6.1f}".format(int(innodb_status['uncheckpointed_bytes'])/1024)+'k','yellow',end='')
             else:
                cprint("{:>6.1f}".format(int(innodb_status['uncheckpointed_bytes']))+'b','yellow',end='')
             cprint("{:>6.0f}{:>7.0f}{:>5.0f}".format(int(innodb_status['read_views']),int(innodb_status['queries_inside']),int(innodb_status['queries_queued'])),'white',end='')
             cprint('|','green',attrs=['bold'],end='')
          if threads:
              cprint("{:>4.0f}{:>5.0f}{:>5.0f}{:>5.0f}".format(int(mystat2["Threads_running"]),int(mystat2["Threads_connected"]),threads_created_diff,int(mystat2["Threads_cached"])),'white',end='')
              cprint('|','green',attrs=['bold'],end='')
          if bytes:
             if bytes_received_diff/1024/1024>1:
                cprint("{:>6.1f}".format(bytes_received_diff/1024/1024)+'m','white',end='')
             elif bytes_received_diff/1024>1:
                  cprint("{:6.0f}".format(bytes_received_diff/1024)+'k','white',end='')
             else:
                  cprint("{:>6.0f}".format(bytes_received_diff)+'b','white',end='')
             if bytes_sent_diff/1024/1024>1:
                  cprint("{:>6.1f}".format(bytes_sent_diff/1024/1024)+'m','white',end='')
             elif bytes_sent_diff/1024>1:
                  cprint("{:6.0f}".format(bytes_sent_diff/1024)+'k','white',end='')
             else:
                  cprint("{:>6.0f}".format(bytes_sent_diff)+'b','white',end='')
             cprint('|','green',attrs=['bold'],end='')
       else:
          if com:
              cprint ("{:>5d}{:>6d}{:>6d}".format(0,0,0),'white',end='')
              cprint ("{:>7d}{:>6d}".format(0,0),'yellow',end='')
              cprint('|','green',attrs=['bold'],end='')
          if innodb_hit:
             cprint("{:>7d}".format(0),'white',end='')
             cprint("{:>8.2f}".format(100.00),'green',end='')
             cprint('|','green',attrs=['bold'],end='')
          if innodb_rows:
             cprint("{:>5.0f}{:>6.0f}{:>6.0f}{:7.0f}".format(0,0,0,0),'white',end='')
             cprint('|','green',attrs=['bold'],end='')
          if innodb_pages:
             cprint("{:>7.0f}{:>7.0f}".format(0,0),'white',end='')
             cprint("{:>7.0f}{:>6.0f}".format(0,0),'yellow',end='')
             cprint('|','green',attrs=['bold'],end='')
          if innodb_data:
             cprint ("{:>6.0f}{:>7.0f}{:>6.0f}{:>8.0f}".format(0,0,0,0),'white',end='')
             cprint('|','green',attrs=['bold'],end='')
          if innodb_log:
             cprint ("{:>6.0f}".format(0),'white',end='')
             cprint ("{:>8.0f}".format(0),'yellow',end='')
             cprint('|','green',attrs=['bold'],end='')
          if innodb_status:
             cprint("{:>5d}".format(0),'white',end='')
             cprint("{:>6.1f}".format(0)+'b','yellow',end='')
             cprint("{:>6.1f}".format(0)+'b','yellow',end='')
             cprint("{:>6d}{:>7d}{:>5d}".format(0,0,0),'white',end='')
             cprint('|','green',attrs=['bold'],end='')
          if threads:
             cprint("{:>4.0f}{:>5.0f}{:>5.0f}{:>5.0f}".format(0,0,0,0),'white',end='')
             cprint('|','green',attrs=['bold'],end='')
          if bytes:
             cprint("{:>7.0f}{:>7.0f}".format(0,0),'white',end='')
             cprint('|','green',attrs=['bold'],end='')
    # Keep Last Status
    mystat1 = mystat2
    mysql_no_first += 1
#---------------------------------------------------------------------------
# 15.
# Function:
# ChangeLog:
#---------------------------------------------------------------------------
def get_sysinfo():
    ncpu=multiprocessing.cpu_count()
    if my_load :
        loadavg=load_stat()
        if operator.gt(float(loadavg['lavg_1']),ncpu):
            cprint ("{:5.2f}".format(float(loadavg['lavg_1'])),'red',end='')
        else:
            cprint ("{:5.2f}".format(float(loadavg['lavg_1'])),'white',end='')
        if operator.gt(float(loadavg['lavg_5']),ncpu):
            cprint ("{:6.2f}".format(float(loadavg['lavg_5'])),'red',end='')
        else:
            cprint ("{:6.2f}".format(float(loadavg['lavg_5'])),'white',end='')
        if operator.gt(float(loadavg['lavg_15']),ncpu):
            cprint ("{:6.2f}".format(float(loadavg['lavg_15'])),'red',end='')
        else:
            cprint ("{:6.2f}".format(float(loadavg['lavg_15'])),'white',end='')

        cprint ('|','blue',attrs=['bold'],end='')
    if my_cpu or my_disk is not None :
        cpuinfo=readCpuInfo()
        if my_cpu:
          if operator.gt(cpuinfo['userdiff_t'],10):
             cprint ("{:3d}".format(cpuinfo['userdiff_t']),'red',end='')
          else:
             cprint ("{:3d}".format(cpuinfo['userdiff_t']),'green',end='')
          if operator.gt(cpuinfo['systemdiff_t'],10):
             cprint ("{:4d}".format(cpuinfo['systemdiff_t']),'red',end='')
          else:
             cprint ("{:4d}".format(cpuinfo['systemdiff_t']),'white',end='')
          cprint ("{:4d}".format(cpuinfo['idlediff_t']),'white',end='')
          if operator.gt(cpuinfo['iowaitdiff_t'],10):
             cprint ("{:4d}".format(cpuinfo['iowaitdiff_t']),'red',end='')
          else:
             cprint ("{:4d}".format(cpuinfo['iowaitdiff_t']),'green',end='')
          cprint ('|','blue',attrs=['bold'],end='')
    if my_swap:
        swapinfo=get_swap()
        if swapinfo['pswpin']>0:
            cprint ("{:5d}".format(int(swapinfo['pswpin']/interval)),'red',end='')
        else:
            cprint ("{:5d}".format(0),'white',end='')
        if swapinfo['pswpout']>0:
            cprint ("{:5d}".format(int(swapinfo['pswpout']/interval)),'red',end='')
        else:
            cprint ("{:5d}".format(0),'white',end='')
        cprint ('|','blue',attrs=['bold'],end='')
    if my_net is not None:
       netinfo=readNetInfo(my_net)
       if netinfo is None:
          cprint ('\nERROR! Please set the right net info!\n','red')
          sys.exit(0)
       else:
           #netinfo['recv']=1073741824
           #1048576
           #1073741824
           #netinfo['send']=1073741824
           #1048576
           #1073741824
           if netinfo['recv']/1024/1024>1:
                cprint ("{:>7.1f}".format(netinfo['recv']/1024/1024)+'m','red',end='')
           elif netinfo['recv']/1024>1:
               cprint ("{:>7d}".format(int(netinfo['recv']/1024))+'k','red',end='')
           else:
               cprint ("{:>7d}".format(int(netinfo['recv']))+'b','white',end='')
           if netinfo['send']/1024/1024>1:
               cprint ("{:>7.1f}".format((netinfo['send']/1024/1024))+'m','red',end='')
           elif netinfo['send']/1024>1:
                cprint ("{:>7d}".format(int(netinfo['send']/1024))+'k','red',end='')
                #cprint ('|','blue',end='')
           else:
                cprint ("{:>7d}".format(int(netinfo['send']))+'b','white',end='')
           cprint ('|','blue',attrs=['bold'],end='')
    if my_disk is not None:
           deltams = 1000* (cpuinfo['userdiff'] + cpuinfo['systemdiff'] + cpuinfo['idlediff'] +cpuinfo['iowaitdiff'] ) /ncpu /HZ
           ios_diff=readDiskInfo(my_disk,deltams)
           if ios_diff is None:
              cprint ('\nERROR! Please set the right disk info!\n','red')
              #cprint ('sys_io1:','white',end='')
              #cprint (sys_io1,'red')
              sys.exit(0)
           else:
               #print ios_diff
               cprint ("{:>6.1f}{:>7.1f}".format(ios_diff['rd_ios_s'],ios_diff['wr_ios_s']),'white',end='')
               if ios_diff['rkbs']>1024:
                  cprint("{:>8.1f}".format(ios_diff['rkbs']),'red',end='')
               else:
                  cprint("{:>8.1f}".format(ios_diff['rkbs']),'white',end='')
               if ios_diff['wkbs']>1024:
                  cprint("{:>8.1f}".format(ios_diff['wkbs']),'red',end='')
               else:
                  cprint("{:>8.1f}".format(ios_diff['wkbs']),'white',end='')
               cprint("{:>8.1f}".format(ios_diff['queue']),'white',end='')
               if ios_diff['wait']>5:
                  cprint("{:>6.1f}".format(ios_diff['wait']),'red',end='')
               else:
                  cprint("{:>6.1f}".format(ios_diff['wait']),'green',end='')
               if ios_diff['svc_t']>5:
                  cprint("{:>6.1f}".format(ios_diff['svc_t']),'red',end='')
               else:
                  cprint("{:>6.1f}".format(ios_diff['svc_t']),'white',end='')
               if ios_diff['busy']>80:
                  cprint("{:>8.1f}".format(ios_diff['busy']),'red',end='')
               else:
                  cprint("{:>8.1f}".format(ios_diff['busy']),'green',end='')
               cprint('|','blue',attrs=['bold'],end='')
#---------------------------------------------------------------------------
# 16.
# Function:
# ChangeLog:
#---------------------------------------------------------------------------
def get_dbrt():
    my_pid=os.getpid()
    tcprstat_lck = 'orzdba_tcprstat.'+str(my_pid)
    lock_file=tcprstat_dir+tcprstat_lck
    try:
       os.open(lock_file, os.O_CREAT|os.O_EXCL|os.O_RDWR)
    except OSError:
       #lock文件已经创建
       s='tail -n 1 '+tcprstat_logfile
       p=subprocess.Popen(s,shell=True,stdout=subprocess.PIPE,bufsize=0)
       out=p.communicate()[0]
       if out:
           (timestamp,count,max,min,avg,med,stddev,max_95,avg_95,std_95,max_99,avg_99,std_99)=out.split()
           cprint("{:>7.0f}".format(int(count)),'green',end='')
           if int(avg) >10000:
               cprint("{:>7.0f}".format(int(avg)),'red',end='')
           else:
               cprint("{:>7.0f}".format(int(avg)),'green',end='')
           if int(avg_95) >10000:
               cprint("{:>7.0f}".format(int(avg_95)),'red',end='')
           else:
               cprint("{:>7.0f}".format(int(avg_95)),'green',end='')
           if int(avg_99) >10000:
               cprint("{:>7.0f}".format(int(avg_99)),'red',end='')
           else:
               cprint("{:>7.0f}".format(int(avg_99)),'green',end='')
       else:
           #cprint('out:'+str(len(out)))
           cprint("{:>7.0f}{:>7.0f}{:>7.0f}{:>7.0f}".format(0,0,0,0),'green',end='')
       cprint('|','green',attrs=['bold'],end='')
    else:
       #第一次运行
       pid = os.fork()
       if pid==0:
          chpid=os.getpid()
          #tcprstat_logfile=tcprstat_dir+'orzdba_tcprstat.'+str(chpid)+'.log'
          my_tcprstat='/usr/bin/tcprstat --no-header -t 1 -n 0 -p '+my_port+' -l '+get_ip_address()
          my_tcprstat+= ' >'+tcprstat_dir+'orzdba_tcprstat.'+str(chpid)+'.log'
          #print my_tcprstat
          os.execlp("/bin/sh", "sh", "-c",my_tcprstat)
          sys.exit(0)
       tcprstat_logfile=tcprstat_dir+'orzdba_tcprstat.'+str(pid)+'.log'
       cprint("{:>7.0f}{:>7.0f}{:>7.0f}{:>7.0f}".format(0,0,0,0),'green',end='')
       cprint('|','green',attrs=['bold'],end='')

#---------------------------------------------------------------------------
# 17.
# Function: 主程序入口
# ChangeLog:
#---------------------------------------------------------------------------
def main():
    #variables
    mycount = 0
    signal.signal(signal.SIGINT,catch_zap)
    python_version=sys.version_info
    if python_version<(2,7):
       sys.exit('error: Python 2.7 or later required')
    #clean screen
    os.system('cls' if os.name == 'nt' else 'clear')
    #cprint (str(python_version))
    opts=get_options()
    if optflag==0:sys.exit(0)
    mysql_conn='mysql -s --skip-column-names -uroot -P'+my_port
    if my_socket is not None:
       mysql_conn +=' -S'+my_socket
    #print mysql_conn
    if orz_logfile is not None:
       HAS_COLOR=1
       cprint('--------write log begin--------------------------','green',end='')
       cprint('')
       old_console= sys.stdout
       if logfile_by_day:
          #logfile=orz_logfile+'.'+time.strftime('%Y%m%d%H%M',time.localtime(time.time()))
          logfile=orz_logfile+'.'+time.strftime('%Y%m%d',time.localtime(time.time()))
       else:
          logfile=orz_logfile
       cprint('logfile:'+logfile,'green',end='')
       cprint('')
       HAS_COLOR=0
       sys.stdout = open(logfile,'w+')
    Print_title()
    while(1):
        #-C:Times to exists
        if (count is not None and mycount+1>count):break
        if (orz_logfile is not None and logfile_by_day):
            newlogfile=orz_logfile+'.'+time.strftime('%Y%m%d',time.localtime(time.time()))
            if os.path.exists(newlogfile)==False:
                logfile=newlogfile
                cprint(logfile)
                sys.stdout.close
                sys.stdout=open(logfile,'w+')
                Print_title()
                if count is not None:
                   count =count - mycount
                   mycount = 0
        # Print Headline
        if ( mycount%15 == 0 ):
            if mysql:
               cprint(headline1,end='')
               cprint (mysql_headline1)
               cprint (headline2,end='')
               cprint(mysql_headline2)
            else:
               cprint(headline1)
               cprint(headline2)
        mycount+=1
        # (1) Print Current Time
        if (timeFlag == 1):
            cprint (colored(time.strftime("%H:%M:%S", time.localtime()),'yellow')+colored('|','blue',attrs=['bold']),end='')
        # (2) Print SysInfo
        get_sysinfo()
        # (3) Print MySQL Status
        get_mysqlstat()
        #(4) TCPRSTAT
        if dbrt:
           get_dbrt()
        cprint ('')
        #sleep interval
        time.sleep(interval)
if __name__ == '__main__':
    main()
