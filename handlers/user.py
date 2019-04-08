#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
用户api
"""

from tornado import gen
import tornado.web
from View import BaseHandler

USER_STATUS = {  # 用户表status字段释义
    "0": "locked",  # 被锁定用户
    "1": "normal",  # 正常用户
    "10": "admin"  # 管理员
}
