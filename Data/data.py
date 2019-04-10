#!/usr/bin/env python
# encoding:utf8

"""
Watch_Dogs
业务逻辑
"""

from tornado import gen

from conf import setting, encrypt
from models import db_opreation_async
from models.SQL_generate import SQL

Setting = setting.Setting()
logger_data = Setting.logger

USER_STATUS = {  # 用户表status字段释义
    "-1": "游客",
    "0": "被锁定",
    "1": "普通用户",
    "10": "管理员"
}


class Data(object):
    """业务逻辑处理"""
    # Singleton
    _instance = None

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(Data, cls).__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        self.db = db_opreation_async.AsyncDataBase()
        self.prpcrypt = encrypt.Prpcrypt()

    @gen.coroutine
    def check_login(self, **json):
        """验证登陆,并更新最后登陆时间"""
        res = yield self.db.query_one(SQL.check_login(json["user"], self.prpcrypt.encrypt(json["password"])))
        if not res:
            logger_data.warning("login failed. details:" + str(json))
            raise gen.Return((None, None, None))
        else:
            yield self.db.execute(SQL.update_user_login_time(res["user_id"]))
            raise gen.Return((str(res["user_id"]), res["user"], str(res["status"])))

    @gen.coroutine
    def create_user(self, **json):
        """用户注册"""
        res = yield self.db.query_one(SQL.select_user_by_name(json["user"]))
        if not res["COUNT(*)"]:
            yield self.db.execute(SQL.create_user(json["user"], self.prpcrypt.encrypt(json["password"])))
            raise gen.Return({"register": True})
        else:  # 已有同名用户
            raise gen.Return({"register": False, "reason": "user name already exist"})

    @gen.coroutine
    def update_user_info(self, uid, update_field, update_value):
        """更新用户信息"""
        if update_field == "password":
            yield self.db.execute(SQL.update_user_info(uid, update_field, self.prpcrypt.encrypt(update_value)))
        else:
            yield self.db.execute(SQL.update_user_info(uid, update_field, update_value))

    @gen.coroutine
    def admin_user_info(self):
        """更新用户信息"""
        res = []
        user_infos = yield self.db.query(SQL.show_all_user())
        for user_info in user_infos:
            r = [user_info["user_id"], user_info["user"], user_info["biref"], user_info["password"],
                 USER_STATUS[str(user_info["status"])]]
            hn = yield self.db.query_one(SQL.get_user_watch_host_num(user_info["user_id"]))
            pn = yield self.db.query_one(SQL.get_user_watch_process_num(user_info["user_id"]))
            r.extend([hn["host_num"], pn["process_num"]])
            res.append(r)
        raise gen.Return(res)
