#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
进程/主机管理相关api
"""

import tornado.web
from tornado import gen

from handlers import BaseHandler
from models.SQL_generate import SQL


class ProcessManage(BaseHandler):
    """/manage/process"""

    @gen.coroutine
    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        try:
            request = self.get_request_json()
            if request["type"] == "close":  # 关闭进程
                res = yield self.data.close_process(request["process_id"], request["pid"])
                self.finish(res)
            elif request["type"] == "restart":  # 重启进程
                res = yield self.data.restart_process(request["process_id"], request["pid"])
                if "host_id" in res:
                    # todo : 添加更多的进程查找规则, 目前只有形如 nohup python -u abc.py & ...的python进程能自动获取新的进程号
                    # just4python process
                    if "python" in res["start_com"]:
                        process_search_name = res["start_com"].replace("nohup", ""). \
                            replace("&", "").replace("python", "").replace("-u", "").strip()  # 去除掉一些无用关键词
                        # 获取新的 pid
                        update_pid = -1
                        process_list = self.remote_api.get_all_process(res["host_id"])
                        for pid, pname in process_list.items():
                            if process_search_name in pname:
                                update_pid = pid  # 找到对应的进程号 (若有多个, 最大的一般是最新的)
                        yield self.db.execute(SQL.update_process_pid(request["process_id"], update_pid))
                        if update_pid != -1:
                            self.remote_api.update_remote_api_conf()  # 重新读取数据库,构建远程客户端连接
                            sql1, sql2 = self.remote_api.update_new_process(res["host_id"], update_pid)
                            yield self.db.execute(sql1)
                            yield self.db.execute(sql2)
                        res["result"] += " 新进程号为 {pid}".format(pid=update_pid)
                    self.finish(res)
                else:  # 出现错误, 提示前段
                    self.finish(res)
        except Exception as err:
            self.finish({"error": str(err)})


class AllHostHandler(BaseHandler):
    """/host/all"""

    @gen.coroutine
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        """用户所有关联主机"""
        res = yield self.data.all_user_host_relation(self.uid)
        if "relation" in res:
            for hr in res["relation"]:
                hr["select_str"] = hr["select_str"].split(" - ")[0].strip()
            self.finish(res)
        else:
            self.finish({"error": "user dont have any host"})


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
