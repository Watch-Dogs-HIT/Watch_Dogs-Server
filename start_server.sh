#!/bin/sh
# 检测远程客户端是否启动
echo "============= 当前路径:" `pwd`
echo -n `date "+%Y-%m-%d %H:%M:%S"` "============= Web服务器进程状态 : "
if test $( ps ax | grep Watch_Dogs-Server.py | grep -v grep | wc -l ) -eq 1;
then
    echo "Web服务器进程已存在"
else
    nohup python -u Watch_Dogs-Server.py &
    echo "启动web服务器"
fi
echo -n `date "+%Y-%m-%d %H:%M:%S"` "============= 远程客户端管理进程状态 : "
if test $( ps ax | grep client_manage.py | grep -v grep | wc -l ) -eq 1;
then
    echo "客户端管理进程已存在"
else
    nohup python -u client_manage.py &
    echo "启动远程客户端管理进程"
fi

echo -n `date "+%Y-%m-%d %H:%M:%S"` "============= 邮件告警进程状态 : "
if test $( ps ax | grep alert_manage.py | grep -v grep | wc -l ) -eq 1;
then
    echo "邮件告警进程已存在"
else
    nohup python -u alert_manage.py &
    echo "启动邮件告警进程"
fi

