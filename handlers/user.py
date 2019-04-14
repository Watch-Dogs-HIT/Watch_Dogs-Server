#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
用户api
"""

import tornado.web
from tornado import gen

from handlers import BaseHandler

USER_STATUS = {  # 用户表status字段释义
    "visitor": "-1",  # 游客
    "locked": "0",  # 被锁定用户
    "normal": "1",  # 正常用户
    "admin": "10"  # 管理员
}


class AuthenticationHandler(BaseHandler):
    """/login"""

    @gen.coroutine
    def get(self, *args, **kwargs):
        return self.render("login.html")

    @gen.coroutine
    def post(self, *args, **kwargs):
        """登录"""
        try:
            json = self.get_json()
            next_url = self.get_argument("next", default="/")
            yield self.data.check_login(**json)
            uid, user, user_status = yield self.data.check_login(**json)
            if user_status == USER_STATUS["locked"]:
                self.finish({"login": False, "msg": "用户被锁定,请联系管理员"})
            elif uid:
                self.set_cookie('uid', uid)
                self.set_cookie('user', user)
                self.set_cookie('user_status', user_status)
                self.finish({"login": True, "next_url": next_url})
            else:
                self.finish({"login": False, "msg": "用户名/密码错误"})
        except Exception as err:
            self.finish({"login": False, "msg": "登陆异常", "error": str(err)})

    @tornado.web.authenticated
    def delete(self, *args, **kwargs):
        """登出"""
        # 必须登陆之后才能登出,否则会 HTTP 403: Forbidden
        self.clear_all_cookies()
        self.finish({"logout": True})


class UserHandler(BaseHandler):
    """/user"""

    @gen.coroutine
    @tornado.web.authenticated
    def get(self, *args, **kwargs):

        yield self.update_cookie()
        raise gen.Return(self.render("user.html"))

    @gen.coroutine
    def post(self, *args, **kwargs):
        """注册"""
        try:
            json = self.get_json()
            if "user" in json and "password" in json:
                res = yield self.data.create_user(**json)
                self.log.info(json["user"] + " registered")
                self.finish(res)
            else:
                self.finish({"error": "no enough params"})
        except Exception as err:
            self.finish({"error": str(err)})

    @gen.coroutine
    @tornado.web.authenticated
    def put(self, *args, **kwargs):
        """更新用户信息"""
        try:
            json = self.get_json()
            if "update_field" in json and "update_value" in json and "update_uid" in json:
                if set(json["update_field"]) < set(["brief", "password", "status"]):
                    yield self.data.update_user_info(json["update_uid"], json["update_field"], json["update_value"])
                    self.log.info("User uid(" + self.uid + ") update " + str(json["update_field"]))
                    self.finish({"updated": json["update_field"]})
                else:
                    self.finish({"error": "illegal update field"})
            else:
                self.finish({"error": "no enough params for update"})
        except Exception as err:
            self.finish({"error": str(err)})


class AdminHandler(BaseHandler):
    """/user/admin"""

    @gen.coroutine
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        """所有用户信息"""
        # uid, user, biref, password, status, host_num, process_num
        res = yield self.data.admin_user_info()
        self.finish({"res": res})
