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
            host_exist = yield self.data.check_host_watched(json["new_process_at_host_id"])
            if host_exist:
                process_exist = yield self.data.check_process_watched(json["new_process_at_host_id"],
                                                                      json["new_process_pid"])
                if not process_exist:  # 进程未存在
                    yield self.data.add_process(**json)
                    yield self.data.add_user_process_relation(self.uid, **json)
                    # 利用远程客户端填充首页数据
                    self.remote_api.update_remote_api_conf()  # 重新读取数据库,构建远程客户端连接
                    self.remote_api.add_new_process(json["new_process_at_host_id"], json["new_process_pid"])
                    self.log.info("add process pid(" + json["new_process_name"] + ", pid=" + str(
                        json["new_process_pid"]) + ") @ No." + json["new_process_at_host_id"] + " host.")
                    self.finish({"status": "添加成功"})
                else:  # 进程已经存在
                    yield self.data.add_user_process_relation(self.uid, **json)
                    # 利用远程客户端填充首页数据
                    self.remote_api.update_remote_api_conf()  # 重新读取数据库,构建远程客户端连接
                    self.remote_api.add_new_process(json["new_process_at_host_id"], json["new_process_pid"])
                    self.finish({"status": "进程已经存在, 添加了当前用户与进程的关系"})
            else:  # 主机未监控
                self.finish({"error": "unknown host, please add host first"})

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
            self.finish({"error": str(err)})

    @gen.coroutine
    @tornado.web.authenticated
    def delete(self, process_id):
        """不再关注进程"""
        try:
            yield self.data.delete_process(self.uid, process_id)
            self.finish({"status": "delete " + str(process_id) + " process OK"})
        except Exception as err:
            self.finish({"error": str(err)})


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
            self.finish({"error": str(err)})
