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


class AllHostHandler(BaseHandler):
    """/host/all"""

    @gen.coroutine
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        """用户所有关联主机"""
        res = yield self.data.all_user_host_relation(self.uid)
        for hr in res["relation"]:
            hr["select_str"] = hr["select_str"].split(" - ")[0].strip()
        # just 4 test
        from copy import deepcopy
        res["relation"].append(deepcopy(res["relation"][0]))
        res["relation"][1]["select_str"] = "#13 : houjie@10.245.146.202"
        res["relation"][1]["host_id"] = 13
        self.finish(res)


class AllProcessHandler(BaseHandler):
    """/process/all"""

    @gen.coroutine
    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        """某主机上运行的所有进程及名称"""
        try:
            request = self.get_request_json()
            if "host_id" in request:
                self.finish(self.remote_api.get_all_process(request["host_id"]))
            else:
                self.finish({"error": "no enough params for process all"})
        except Exception as err:
            self.finish({"error": str(err)})
