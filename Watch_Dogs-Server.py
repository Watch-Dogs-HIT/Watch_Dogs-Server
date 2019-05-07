#!/usr/bin/env python
# encoding:utf-8

"""
Watch_Dogs
基于Linux远程主机及进程状态监测系统 - 服务端入口

@author : h-j-13
@github : https://github.com/Watch-Dogs-HIT/Watch_Dogs-Server
@date   : 2019-5
"""

import os.path

import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpserver
import tornado.autoreload

from url import HANDLERS
from conf import setting

from Data import data
from models import db_opreation_async
from client_manage import ClientManager
from Data.alert_monitor import AlertMonitor

Setting = setting.Setting()


def createApp():
    SETTINGS = {
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        # "cookie_secret": "Watch_Dogs",
        "login_url": "/login",
        "debug": True,  # debug mode
    }

    app = tornado.web.Application(
        handlers=HANDLERS,
        **SETTINGS
    )

    app.db = db_opreation_async.AsyncDataBase()
    app.log = Setting.logger
    app.data = data.Data()
    app.setting = Setting
    app.remote_api = ClientManager()
    app.alert_monitor = AlertMonitor()
    return app


tornado.options.parse_command_line()
app = createApp()

if __name__ == '__main__':
    # # Alert Demo
    # AlertMonitor().alert_monitor_thread()

    # Web Server
    server = tornado.httpserver.HTTPServer(app)
    server.listen(Setting.PORT)
    tornado.ioloop.IOLoop.current().start()
