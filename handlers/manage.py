#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
进程/主机管理相关api
"""

import tornado.web
from tornado import gen

from handlers import BaseHandler


class HostManage(BaseHandler):
    """/manage/host"""

    @gen.coroutine
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        pass


class ProcessManage(BaseHandler):
    """/manage/process"""

    @gen.coroutine
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        pass


class AllProcessHandler(BaseHandler):
    """/process/all"""

    @gen.coroutine
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        pass
