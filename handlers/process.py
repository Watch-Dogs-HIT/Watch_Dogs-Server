#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
进程相关api
"""
import tornado.web
from tornado import gen

from handlers import BaseHandler


class ProcessHandler(BaseHandler):
    """/process"""

    @gen.coroutine
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        return self.render("process.html")

    @gen.coroutine
    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        """添加进程"""
        try:
            json = self.get_json()
            if "host" in json and "pid" in json and "comment" in json and "type" in json:
                host_exist = yield self.data.check_host_watched(json["host"])
                if host_exist:
                    process_exist = yield self.data.check_process_watched(json["host"], json["pid"])
                    if not process_exist:
                        res = yield self.data.add_process(self.uid, **json)
                        self.log.info("add process pid(" + json["pid"] + ") @ " + json["host"])
                        self.finish(res)
                    else:
                        self.finish({"error": "process already watched"})
                else:
                    self.finish({"error": "unknown host, please add host first"})
            else:
                self.finish({"error": "no enough params"})
        except Exception as err:
            self.finish({"error": str(err)})


class ProcessInfoHandler(BaseHandler):
    """/process/([0-9]+)"""

    @gen.coroutine
    @tornado.web.authenticated
    def get(self, process_id):
        """进程信息"""
        record_num = self.get_argument("num", default=30)
        res = yield self.data.get_process_record(process_id, record_num)
        self.finish(res)

    @gen.coroutine
    @tornado.web.authenticated
    def put(self, process_id):
        """更新进程信息"""

    @gen.coroutine
    @tornado.web.authenticated
    def delete(self, process_id):
        """不再关注进程"""