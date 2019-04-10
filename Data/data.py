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

    # USER

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
            r = [user_info["user_id"], user_info["user"], user_info["brief"], user_info["password"],
                 USER_STATUS[str(user_info["status"])]]
            hn = yield self.db.query_one(SQL.get_user_watch_host_num(user_info["user_id"]))
            pn = yield self.db.query_one(SQL.get_user_watch_process_num(user_info["user_id"]))
            r.extend([hn["host_num"], pn["process_num"]])
            res.append(r)
        raise gen.Return(res)

    # Index
    @gen.coroutine
    def index_data(self, uid):
        """首页个人资源"""
        # 监测的总主机数, 监测的总进程数, 正常/总进程数, 异常日志数
        res = {
            "host_num": -1,
            "process_num": -1,
            "normal_process_num": -1,
            "error_log_num": -1,
        }
        hn = yield self.db.query_one(SQL.get_user_watch_host_num(uid))
        pn = yield self.db.query_one(SQL.get_user_watch_process_num(uid))
        watch_process_infos = yield self.db.query(SQL.get_user_watch_process(uid))
        error_logs = -1  # todo : yield self.db.query(...)
        # for user_info in user_infos:
        #     r = [user_info["user_id"], user_info["user"], user_info["brief"], user_info["password"],
        #          USER_STATUS[str(user_info["status"])]]
        #     hn = yield self.db.query_one(SQL.get_user_watch_host_num(user_info["user_id"]))
        #     pn = yield self.db.query_one(SQL.get_user_watch_process_num(user_info["user_id"]))
        #     r.extend([hn["host_num"], pn["process_num"]])
        #     res.append(r)
        # raise gen.Return(res)

    @gen.coroutine
    def check_host_watched(self, host):
        """查询主机是否被检测"""
        res = yield self.db.query_one(SQL.check_host_watched(host))
        raise gen.Return(res["host_exist"])

    # Process
    @gen.coroutine
    def check_process_watched(self, host, pid):
        """查询进程是否被检测"""
        res = yield self.db.query_one(SQL.check_process_watched(host, pid))
        raise gen.Return(res["process_exist"])

    @gen.coroutine
    def add_process(self, uid, **json):
        """增加进程"""
        host_id = yield self.db.query_one(SQL.get_host_id(json["host"]))
        yield self.db.execute(SQL.add_watch_process(json["host"], json["pid"]))
        process_id = yield self.db.query_one(SQL.get_process_id(json["host"], json["pid"]))
        yield self.db.execute(SQL.add_user_process_relation(
            uid, host_id["host_id"], process_id["process_id"], json["comment"], json["type"]
        ))
        relation_id = yield self.db.query_one(SQL.get_user_process_relation_id(uid,
                                                                               host_id["host_id"],
                                                                               process_id["process_id"])
                                              )
        res = {
            "host_id": host_id["host_id"],
            "process_id": process_id["process_id"],
            "relation_id": relation_id["relation_id"],
            "process_type": "/".join([json["comment"], json["type"]])
        }
        raise gen.Return(res)
