#!/usr/bin/env python
# encoding:utf-8


import time
import os.path

from collections import namedtuple
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options

from tornado.options import define, options

define("port", default=8001, help="run on the given port", type=int)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("username")

    @property
    def uid(self):
        return self.get_secure_cookie("id")


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        # 设置cookie例子 设置多个
        self.set_secure_cookie("username", self.get_argument("username"))
        self.set_secure_cookie("id", "12")
        self.set_secure_cookie("test", "323")
        self.redirect("/")


class WelcomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # 读取多个cookie,不同方式
        self.render('test.html', user=self.current_user,
                    id=self.uid,
                    test=self.get_secure_cookie("test"))
        # 尝试读取不存在的cookie;不存在返回none
        print self.get_secure_cookie("111")


class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # 清除所有　cookie
        self.clear_all_cookies()
        self.render('logout.html', user=self.current_user)


if __name__ == "__main__":
    # tornado.options.parse_command_line()

    settings = {
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "cookie_secret": "Watch_Dogs",
        "xsrf_cookies": True,  # 启用XSRF防护
        "login_url": "/login"
    }

    # 启用XSRF防护方法:
    # 在HTML页面添加相关的代码
    # <form action="/new_message" method="post">
    #     {% module xsrf_form_html() %}
    #     ......
    # </form>

    application = tornado.web.Application([
        (r'/', WelcomeHandler),
        (r'/login', LoginHandler),
        (r'/logout', LogoutHandler)
    ], **settings)

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
