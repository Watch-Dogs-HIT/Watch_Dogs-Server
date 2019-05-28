#!/bin/sh
# 检测远程客户端是否启动
echo "============= 当前路径:" `pwd`
echo -n `date "+%Y-%m-%d %H:%M:%S"` "============= 进程状态 : "
if test $( ps ax | grep Watch_Dogs-Client.py | grep -v grep | wc -l ) -eq 1;
then
    echo "[错误] 监控进程已存在, 请继续之后的步骤即可"
    return 0
else
    echo "监控进程未存在"
fi
# 检测默认python版本
echo -n `date "+%Y-%m-%d %H:%M:%S"` "============= 检测默认python版本 : "
if test $( python -V 2>&1 | awk '{print $2}' | awk -F '.' '{print $1}' ) -eq 2;
then
    echo "当前Python版本" `python -V 2>&1 | awk '{print $2}'`
else
    echo "[错误] 当前是Python3环境, 远程监控客户端尚未支持Python3. 请改用Python2进行安装部署"
    return 0
fi
# 检测系统压缩包, 文件夹是否存在
echo -n `date "+%Y-%m-%d %H:%M:%S"` "============= 检测系统文件夹 : "
if [ ! -d ".Watch_Dogs-Client" ]
then
    # python解释器提权
    local_path=`pwd`
    cd /usr/bin
    sudo setcap cap_kill,cap_net_raw,cap_dac_read_search,cap_sys_ptrace+ep ./python2.7
    cd $local_path
    # 下载客户端
    echo "不存在"
    echo `date "+%Y-%m-%d %H:%M:%S"` "============= 部署系统文件夹, 当前路径为" `pwd`
    wget http://10.245.146.202:8013/client/Watch_Dogs-Client.tar.gz
    tar -xvf Watch_Dogs-Client.tar.gz
    mv Watch_Dogs-Client-master .Watch_Dogs-Client
    cd .Watch_Dogs-Client
    # 安装依赖环境
    sudo apt-get install python-pip -y  # 不兼容yum...
    echo `date "+%Y-%m-%d %H:%M:%S"` "============= 使用pip部署安装环境, 当前PIP版本 : " `pip -V 2>&1`
    sudo pip install Flask
    sudo pip install tornado
    # 网络监控能力
    echo `date "+%Y-%m-%d %H:%M:%S"` "============= 部署系统网络监控能力 - nethogs"
    sudo apt-get install build-essential libncurses5-dev libpcap-dev -y
    sudo apt-get install git -y
    git clone https://github.com/raboof/nethogs.git
    cd nethogs && make libnethogs && sudo make install_dev
    # 启动检测进程
    cd ..
    nohup sh RunClient.sh &
    echo `date "+%Y-%m-%d %H:%M:%S"` "============= 监控客户端启动完成"
else
    echo "系统安装包已经存在, 请检查系统是否已经部署, 重启监控进程..."
    cd .Watch_Dogs-Client
    nohup sh RunClient.sh &
    echo `date "+%Y-%m-%d %H:%M:%S"` "============= 监控客户端启动完成, 检测脚本启动完成"
fi