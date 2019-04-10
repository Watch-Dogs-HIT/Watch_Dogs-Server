#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
路由配置
"""

from handlers import *
from handlers.user import *
from handlers.host import *
from handlers.index import *
from handlers.process import *

# 路由配置
HANDLERS = [
    (r'/v', TestHandler),  # version
    (r'/', IndexHandler),  # 首页
    (r'/login', AuthenticationHandler),  # 登录,注销
    (r'/user', UserHandler),  # 注册,更新
    (r'/user/admin', AdminHandler),  # 管理
    (r'/index', IndexDataHandler),  # 首页资源
    (r'/host', HostHandler),  # 主机
    (r'/host/([0-9]+)', HostInfoHandler),  # 主机信息
    (r'/process', ProcessHandler),  # 进程
    (r'/process/([0-9]+)', ProcessInfoHandler)  # 进程信息
]
