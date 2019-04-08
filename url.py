#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
路由配置
"""

from handlers import *
from handlers.user import *

HANDLERS = [
    (r'/', IndexHandler),
    (r'/login', AuthenticationHandler),  # 登录,注销
    (r'/user', UserHandler),  # 注册,更新
    (r'/index', IndexHandler),
    (r'/host', IndexHandler),
    (r'/process', IndexHandler),
]
