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
    def post(self, *args, **kwargs):
        try:
            request = self.get_request_json()
            if "host_id" in request:
                self.finish(self.remote_api.get_all_process(request["host_id"]))
            else:
                self.finish({"error": "no enough params for process all"})
        except Exception as err:
            print err
            self.finish({"error": str(err)})
