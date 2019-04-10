#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
用户api
"""

import tornado.web
from tornado import gen

from handlers import BaseHandler


class IndexHandler(BaseHandler):
    """/"""

    @gen.coroutine
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        return self.render("index.html")


class IndexDataHandler(BaseHandler):
    """/index"""

    @gen.coroutine
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        """首页相关信息"""
        print self.uid
