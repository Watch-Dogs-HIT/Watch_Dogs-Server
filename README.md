
# Watch_Dogs 
![image.png](https://upload-images.jianshu.io/upload_images/5617720-3077d2a479b8b021.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

Watch_Dogs 是一个CS架构, 底层基于Linux /proc文件系统的, 通过Python实现的远程Linux主机及进程的监控系统. 用户可以通过Web页面轻松地完成对于多台远程Linux主机的资源占用监控、进程资源占用监控、进程管理、日志分析及进程资源预警的功能.    

## 部署
#### 环境要求
**Python 2**
使用pip安装运行环境

方法1. 使用requirements.txt一键配置
进入项目文件夹后, 执行`pip install -r requirements.txt`命令

方法2.  使用pip手动进行环境配置
执行如下命令
```shell
	pip install requests  
	pip install paramiko  
	pip install pycrypto  
	pip install pymysql  
	pip install PyYAML  
	pip install schedule  
	pip install tornado  
	pip install tormysql
```

**MySQL**
1. 安装MySQL (*无版本要求, 开发过程使用的数据库版本为MySQL 8.0.13*)
2. 配置数据库
利用以备份好的[sql文件]([https://github.com/Watch-Dogs-HIT/Database](https://github.com/Watch-Dogs-HIT/Database))快速部署数据库即可

#### 静态变量配置
进入系统目录, 修改`conf/setting.json` 这个配置文件中的如下几项
```json
{
	...
	"port": 8013,
	"database": {
	"host": "localhost",
	"port": 3306,
	"user": "root",
	"password": "19950705",
	"charset": "utf8mb4",
	"database_name": "Watch_Dogs"
	...
}
```
主要包括, 系统web启动端口, 已经配置好数据的数据库链接参数.

#### 启动
设置好环境和数据库之后, 返回系统目录. 执行
`sh start_server.sh`
即可完成系统启动

尝试访问 `http://{你的ip}:{配置的端口}`, 若出现如下页面. 则代表启动成功, 接下来即可正常使用
![image.png](https://upload-images.jianshu.io/upload_images/5617720-3b07fa9c0b8216ee.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


## WIKI
若想获取更详尽的环境配置, 异常处理, 各个功能的使用说明.    
请参见该项目 [中文wiki]([https://github.com/Watch-Dogs-HIT/Watch_Dogs-Server/wiki](https://github.com/Watch-Dogs-HIT/Watch_Dogs-Server/wiki))

## 各部分源码地址
下面是该项目的所有源码地址

1. [Watch_Dogs Server](https://github.com/Watch-Dogs-HIT/Watch_Dogs-Server) - 服务端, Web服务与远程客户端管理
2. [Watch_Dogs Client](https://github.com/Watch-Dogs-HIT/Watch_Dogs-Client) - 远程客户端, 实现主机及进程监控 
3. Watch_Dogs [Database](https://github.com/Watch-Dogs-HIT/Database) - 数据库, 数据库设计文档及备份
4. [Watch_Dogs](https://github.com/Watch-Dogs-HIT/Watch_Dogs) - 核心功能代码及文档
5. Watch_Dogs [Doc](https://github.com/Watch-Dogs-HIT/Doc) - 相关文档
6. [Watch_Dogs WebTemplate](https://github.com/Watch-Dogs-HIT/WebTemplate) - 前端模板
## 项目名称来源
项目名称及LOGO来自于Ubisoft与2014年发布的动作冒险游戏 [Watch Dogs](https://www.ubisoft.com/en-us/game/watch-dogs/)


## License
WTFPL License

## 最后
这是一个非常不成熟的项目, 如果你准备使用这套系统.    
我非常建议你通读源码, 可能有很多地方值得你来进行改进.    
如果你有任何想法的话, 也非常欢迎你来和我交流.    
我的邮箱地址 h.j.13.new@gmail.com   

h-j-13
