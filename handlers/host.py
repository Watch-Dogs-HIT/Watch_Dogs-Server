#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
主机相关api
"""

import tornado.web
from tornado import gen

from handlers import BaseHandler


class HostHandler(BaseHandler):
    """/host"""

    @gen.coroutine
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        return self.render("host.html")

    @gen.coroutine
    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        """添加主机"""


class HostInfoHandler(BaseHandler):
    """/host/([0-9]+)"""

    @gen.coroutine
    @tornado.web.authenticated
    def get(self, host_id):
        """主机信息"""

        if host_id == "0":  # 获取所有主机
            res = yield self.data.all_user_host_relation(self.uid)
            self.finish(res)
        else:
            res = yield self.data.host_index_data(self.uid, host_id)
            self.finish(res)

    @gen.coroutine
    @tornado.web.authenticated
    def put(self, process_id):
        """更新主机信息"""

    @gen.coroutine
    @tornado.web.authenticated
    def delete(self, process_id):
        """删除主机"""
