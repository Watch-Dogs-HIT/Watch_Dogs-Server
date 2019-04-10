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
        return self.render("process.html")

    @gen.coroutine
    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        """添加主机"""


class HostInfoHandler(BaseHandler):
    """/host/([0-9]+)"""

    @gen.coroutine
    @tornado.web.authenticated
    def get(self, host_id):
        """主机资源记录"""
        record_num = self.get_argument("num", default=30)
        res = yield self.data.get_host_record(host_id, record_num)
        self.finish(res)

    @gen.coroutine
    @tornado.web.authenticated
    def put(self, process_id):
        """更新主机信息"""

    @gen.coroutine
    @tornado.web.authenticated
    def delete(self, process_id):
        """删除主机"""
