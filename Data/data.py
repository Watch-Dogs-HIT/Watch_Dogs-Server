#!/usr/bin/env python
# encoding:utf8

"""
Watch_Dogs
业务逻辑
"""

from tornado import gen

from conf import setting
from models import db_opreation_async, SQL_generate

Setting = setting.Setting()
logger_data = Setting.logger


class Data(object):
    """业务逻辑处理"""
    # Singleton
    _instance = None

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(Data, cls).__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        self.db = db_opreation_async.AsyncDataBase()
