#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
路由配置
"""

from handlers import *

HANDLERS = [
    (r'/', IndexHandler),
    (r'/login', IndexHandler),
    (r'/user', IndexHandler),
    (r'/user/set_status', IndexHandler),
    (r'/user/update_password', IndexHandler),

]
