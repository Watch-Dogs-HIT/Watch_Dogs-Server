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
        yield self.update_cookie()
        raise gen.Return(self.render("index.html"))


class IndexDataHandler(BaseHandler):
    """/index"""

    @gen.coroutine
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        """首页相关信息"""
        try:
            # todo : 当一个进程挂掉太久的时候,首页就会报错无法显示数据
            res = yield self.data.index_data(self.uid)
            self.finish(res)
        except Exception as err:
            self.finish({"error": str(err)})
