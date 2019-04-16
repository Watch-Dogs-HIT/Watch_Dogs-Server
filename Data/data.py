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
    def update_cookie(self, uid):
        """根据uid更新用户cookie"""
        res = yield self.db.query_one(SQL.select_status_by_uid(uid))
        raise gen.Return(res["status"] if res else -1)

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
            raise gen.Return({"register": False, "msg": "已经存在的用户名"})

    @gen.coroutine
    def update_user_info(self, uid, update_field, update_value):
        """更新用户信息"""
        for k, v in zip(update_field, update_value):
            if k == "password":
                yield self.db.execute(SQL.update_user_info(uid, k, self.prpcrypt.encrypt(v)))
            else:
                yield self.db.execute(SQL.update_user_info(uid, k, v))

    @gen.coroutine
    def admin_user_info(self):
        """更新用户信息"""
        res = []
        user_infos = yield self.db.query(SQL.show_all_user())
        for user_info in user_infos:
            r = [user_info["user_id"], user_info["user"], user_info["brief"],
                 self.prpcrypt.decrypt(user_info["password"]),
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
            "host": [],
            "host_num": -1,
            "process": [],
            "process_num": -1,
            "un_normal_host": -1,
            "un_normal_host_num": [],
            "un_normal_process": -1,
            "un_normal_process_num": [],
            "error_log_num": -1,
            "recent_host_record": [],
            "recent_process_record": []
        }

        h = yield self.db.query(SQL.get_user_watch_host(uid))
        p = yield self.db.query(SQL.get_user_watch_process(uid))

        res["host"] = h
        res["process"] = p
        res["host_num"] = len(h)
        res["process_num"] = len(p)
        res["error_logs"] = -1  # todo : yield self.db.query(...)
        res["un_normal_process"] = filter(lambda x: x["state"] == u"X", p)
        res["un_normal_process_num"] = len(res["un_normal_process"])
        res["un_normal_host"] = filter(lambda x: x["status"] == 0, h)
        res["un_normal_host_num"] = len(res["un_normal_host"])
        for host_info in h:
            t = {}
            host_id = host_info["host_id"]
            hi = yield self.db.query_one(SQL.get_host_info(host_id))
            hr = yield self.db.query_one(SQL.get_host_recent_record(host_id))
            hrl = yield self.db.query_one(SQL.get_user_host_relation(uid, host_id))
            t.update(hi)
            t.update(hr)
            t.update(hrl)
            t["record_time"] = t["record_time"].strftime('%Y-%m-%d %H:%M:%S')
            t["update_time"] = t["update_time"].strftime('%Y-%m-%d %H:%M:%S')
            res["recent_host_record"].append(t)
        for process_info in p:
            t = {}
            process_id = process_info["process_id"]
            pi = yield self.db.query_one(SQL.get_process_info(process_id))
            pr = yield self.db.query_one(SQL.get_process_recent_record(process_id))
            prl = yield self.db.query_one(SQL.get_user_process_relation(uid, process_id))
            t.update(pi)
            t.update(pr)
            t.update(prl)
            t["record_time"] = t["record_time"].strftime('%Y-%m-%d %H:%M:%S')
            res["recent_process_record"].append(t)
        raise gen.Return(res)

    # Host

    @gen.coroutine
    def check_host_watched(self, host):
        """查询主机是否被检测"""
        res = yield self.db.query_one(SQL.check_host_watched(host))
        raise gen.Return(res["host_exist"])

    @gen.coroutine
    def get_host_record(self, hid, num):
        """获取进程资源记录"""
        records = yield self.db.query(SQL.get_host_records(hid, num))
        host_info = yield self.db.query_one(SQL.get_host_info(hid))
        # 修改datetime数据为str
        for r in records:
            r["record_time"] = r["record_time"].strftime('%Y-%m-%d %H:%M:%S')
        if host_info:
            host_info["update_time"] = host_info["update_time"].strftime('%Y-%m-%d %H:%M:%S')
            host_info["disk_stat"] = eval(host_info["disk_stat"])
            host_info["CPU_info"] = eval(host_info["CPU_info"])

        res = {
            "host_id": hid,
            "host_info": host_info if host_info else {},
            "except_record_num": num,
            "return_record_num": len(records),
            "records": records[1:],
            "now_record": records[0] if records else {}
        }
        raise gen.Return(res)

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

    @gen.coroutine
    def get_process_record(self, pid, num):
        """获取进程资源记录"""
        records = yield self.db.query(SQL.get_process_records(pid, num))
        process_records = yield self.db.query_one(SQL.get_process_record(pid))
        # 修改datetime数据为str
        for r in records:
            r["record_time"] = r["record_time"].strftime('%Y-%m-%d %H:%M:%S')
        if process_records:
            process_records["record_time"] = process_records["record_time"].strftime('%Y-%m-%d %H:%M:%S')

        res = {
            "process_id": pid,
            "process_records": process_records if process_records else {},
            "except_record_num": num,
            "return_record_num": len(records),
            "records": records[1:],
            "now_record": records[0] if records else {}
        }
        raise gen.Return(res)
