#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
base handler
"""

import json
import traceback
import tornado.web
from tornado import gen


def byteify(input_unicode_dict, encoding='utf-8'):
    """
    将unicode字典转为str字典
    reference : https://www.jianshu.com/p/90ecc5987a18
    """
    if isinstance(input_unicode_dict, dict):
        return {byteify(key): byteify(value) for key, value in input_unicode_dict.iteritems()}
    elif isinstance(input_unicode_dict, list):
        return [byteify(element) for element in input_unicode_dict]
    elif isinstance(input_unicode_dict, unicode):
        return input_unicode_dict.encode(encoding)
    else:
        return input_unicode_dict


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
        return self.get_cookie('uid')

    @property
    def user_status(self):
        return self.get_cookie('user_status') if self.get_cookie('user_status') else "-1"

    def get_current_user(self):
        return self.get_cookie("user")

    def get_json(self):
        """解析json"""
        if "Content-Type" in self.request.headers and "application/json" in self.request.headers["Content-Type"]:
            return byteify(json.loads(self.request.body))  # return str dict
        return {"error": "no json found"}

    @gen.coroutine
    def update_cookie(self):
        """更新cookie值"""
        user_status = yield self.data.update_cookie(self.uid)
        self.set_cookie("user_status", str(user_status))

    def write_error(self, status_code, **kwargs):
        """重写错误输出方法"""
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            message = ''
            for line in traceback.format_exception(*kwargs["exc_info"]):
                message += line + '<br>'
            # debug模式错误界面
            self.render(
                'error.html',
                message=message,
                mode='debug'
            )
        else:

            self.render(
                'error.html',
                status_code=status_code,
                message=self._reason,
                mode='produce'
            )


class TestHandler(BaseHandler):
    """/"""

    def get(self):
        return self.render("test.html", date=self.setting.get_local_time(),
                           author="h-j-13",
                           repo_link="https://github.com/Watch-Dogs-HIT/Watch_Dogs-Server")


class NotFoundHandler(BaseHandler):
    """404"""

    def get(self):
        return self.render("404.html", status_code=404)
