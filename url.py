#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
路由配置
"""

from handlers import *
from handlers.user import *
from handlers.index import *
from handlers.host_info import *
from handlers.process_info import *

# 路由配置
HANDLERS = [
    (r'/v', TestHandler),  # version
    (r'/', IndexHandler),  # 首页
    (r'/login', AuthenticationHandler),  # 登录,注销
    (r'/user', UserHandler),  # 注册,更新
    (r'/user/admin', AdminHandler),  # 管理
    (r'/index', IndexHandler),  # 首页资源
    (r'/host', TestHandler),
    (r'/process', TestHandler),
]
