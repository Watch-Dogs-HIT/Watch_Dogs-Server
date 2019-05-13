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
            json = self.get_request_json()
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
        if process_id == "0":  # 获取所有关联进程
            res = yield self.data.all_user_process_relation(self.uid)
            self.finish(res)
        else:
            res = yield self.data.process_index_data(self.uid, process_id)
            self.finish(res)

    @gen.coroutine
    @tornado.web.authenticated
    def put(self, process_id):
        """更新进程信息"""
        try:
            request = self.get_request_json()
            self.data.update_host_info(self.uid, process_id, request)
            self.finish(request)
        except Exception as err:
            print err
            self.finish({"error": str(err)})

    @gen.coroutine
    @tornado.web.authenticated
    def delete(self, process_id):
        """不再关注进程"""
        yield self.data.delete_process(self.uid, process_id)


class ProcessLogHandler(BaseHandler):
    """/log"""

    @gen.coroutine
    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        """进程日志处理"""
        # note : 为什么前后端改成get方法之后json文本就附在url后面了? 使用ajax的get的时候不能传递json?
        # 很多答案是说 GET 的数据须通过 URL 以 Query Parameter 来传送，而 POST 可以通过请求体来发送数据，所以因 URL 的受限，
        # 往往 GET 无法发送太多的字符。这个回答好比在启用了 HTTPS 时，GET 请求 URL 中的参数仍然是明文传输的一样。
        try:
            request = self.get_request_json()
            if "key_word" in request and "host_id" in request and "path" in request:  # 关键词检索
                self.finish(
                    self.remote_api.log_search_keyword(request["host_id"], request["path"], request["key_word"]))
            elif "host_id" in request and "path" in request:  # 日志数据
                self.finish(self.remote_api.log_status(request["host_id"], request["path"]))
            else:
                self.finish({"error": "no enough params for log"})
        except Exception as err:
            print err
            self.finish({"error": str(err)})
