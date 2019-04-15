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
            # todo fin this code
            res = yield self.data.index_data(self.uid)
            self.finish(res)
        except Exception as err:
            self.finish({"error": str(err)})
