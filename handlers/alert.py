#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
预警相关api
"""

import tornado.web
from tornado import gen

from handlers import BaseHandler


class AlertHandler(BaseHandler):
    """/alert"""

    @gen.coroutine
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        """监控预警页面"""
        return self.render("alert.html")

    @gen.coroutine
    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        """用户关联主机/进程及其目前告警信息"""
        return self.render("alert.html")

    @gen.coroutine
    @tornado.web.authenticated
    def put(self, *args, **kwargs):
        """更新预警设置"""
