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
        try:
            request = self.get_request_json()
            res = yield self.data.add_host(self.uid, **request)
            self.finish(res)
        except Exception as err:
            self.finish({"error": str(err)})


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
    def put(self, host_id):
        """更新主机信息"""
        # 更新远程客户端数据
        if str(host_id) not in self.remote_api.client:
            self.remote_api.update_remote_api_conf()  # 重新读取数据库,构建远程客户端连接
        sql1, sql2, host_api_status = self.remote_api.add_new_host(host_id)
        yield self.db.execute(sql1)
        yield self.db.execute(sql2)
        self.finish({"host_id": host_id, "status": host_api_status})

    @gen.coroutine
    @tornado.web.authenticated
    def delete(self, host_id):
        """删除主机"""
        yield self.data.delete_host(self.uid, host_id)
        self.finish({"result": "delete OK"})
