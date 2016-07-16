# 自动上传rpm到各机房的私有源 
支持rpm整个目录上传


#使用方法
   	 rpmupload.py rpm目录 
   
	 rpmupload.py rpm文件

在私有源的机器(一般为cobbler):


	yum install -y supervisor python-webpy python-simplejson
	mkdir -p /data/ops
	cp upload.py /data/ops
	
	修改 /etc/supervisord.conf
	添加
	[program:rpmupload]
	command=/usr/bin/python /data/ops/upload.py
	autostart=true
	autorestart=true
	
	启动
	/etc/init.d/supervisord start
