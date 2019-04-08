#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
view
"""

import json
import datetime
from collections import namedtuple

import tornado.web
from tornado import gen

User = namedtuple("User", "uid username level")


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

    def options(self):
        # no body
        self.set_status(204)
        self.finish()

    @property
    def db(self):
        return self.application.db

    @property
    def data(self):
        return self.application.data

    @property
    def log(self):
        return self.application.log

    @property
    def setting(self):
        return self.application.setting

    def get_current_user(self):
        uid = self.get_secure_cookie('uid')
        nickname = self.get_secure_cookie('nickname')
        account = self.get_secure_cookie('account')
        if uid and nickname and account:
            return User(uid=uid, nickname=nickname, account=account)
        else:
            return None

    def set_default_headers(self):
        """设置响应的默认 HTTP HEADER, 非全局
        """
        headers = dict(
            Server='MY_SERVER',
            Date=datetime.datetime.now()
        )
        for k, v in headers.items():
            self.set_header(k, v)
        cookies = dict(
            foo='foo_cookie',
            bar='bar_cookie'
        )
        for k, v in cookies.items():
            self.set_cookie(k, v, expires_days=7)

    def get_json(self):
        """解析json"""
        if "application/json" in self.request.headers["Content-Type"]:
            return json.loads(self.request.body)
        return {}


class IndexHandler(BaseHandler):
    """/"""

    def get(self):
        self.finish('hello world')
