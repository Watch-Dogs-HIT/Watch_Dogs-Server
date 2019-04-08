#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
base handler
"""

import json
from abc import ABCMeta

import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    """"""

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")  # 这个地方可以写域名
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.set_header("Access-Control-Allow-Credentials", True)

    def post(self):
        pass

    def get(self):
        pass

    @property
    def db(self):
        """异步数据库操作对象"""
        return self.application.db

    @property
    def log(self):
        """日志对象"""
        return self.application.log

    @property
    def data(self):
        """业务逻辑,数据处理"""
        return self.application.data

    @property
    def setting(self):
        """设置对象"""
        return self.application.setting

    @property
    def uid(self):
        return self.get_secure_cookie('uid')

    @property
    def user_status(self):
        return self.get_secure_cookie('user_status') if self.get_secure_cookie('user_status') else "-1"

    def get_current_user(self):
        return self.get_secure_cookie("user")

    def get_json(self):
        """解析json"""
        if "application/json" in self.request.headers["Content-Type"]:
            return json.loads(self.request.body)
        return {}


class IndexHandler(BaseHandler):
    """/"""

    def get(self):
        return self.render("test.html", date=self.setting.get_local_time(),
                           author="h-j-13",
                           repo_link="https://github.com/Watch-Dogs-HIT/Watch_Dogs-Server")
