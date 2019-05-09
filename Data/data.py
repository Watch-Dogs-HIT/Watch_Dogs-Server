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
            yield self.db.execute(SQL.create_user(json["user"], self.prpcrypt.encrypt(json["password"]), json["email"]))
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
                 USER_STATUS[str(user_info["status"])], user_info["email"] if user_info["email"] else "无"]
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
        res["error_logs"] = -1  # TODO : yield self.db.query(...)
        res["un_normal_process"] = filter(lambda x: x["state"] == u"X" or x["state"] == u"0" or x["state"] == 0, p)
        res["un_normal_process_num"] = len(res["un_normal_process"])
        res["un_normal_host"] = filter(lambda x: x["status"] == 0, h)
        res["un_normal_host_num"] = len(res["un_normal_host"])
        # host
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
        # process
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
            t["update_time"] = t["update_time"].strftime('%Y-%m-%d %H:%M:%S')
            res["recent_process_record"].append(t)
        raise gen.Return(res)

    # Host

    @gen.coroutine
    def check_host_watched(self, host):
        """查询主机是否被检测"""
        res = yield self.db.query_one(SQL.check_host_watched(host))
        raise gen.Return(res["host_exist"])

    @gen.coroutine
    def all_user_host_relation(self, user_id):
        """获取所有用户关联主机"""
        res = {}
        # relation
        relations = yield self.db.query(SQL.get_user_all_host_relation(user_id))
        if relations:
            res["relation"] = relations
            for h in res["relation"]:
                hi = yield self.db.query_one(SQL.get_host_info(h["host_id"]))

                select_btn_str = "#" + str(hi["host_id"]) + " : " + hi["user"] + "@" + hi["host"] + \
                                 " - " + h["comment"] + "/" + h["type"]
                h["select_str"] = select_btn_str
            raise gen.Return(res)
        else:
            raise gen.Return({"error": "user dont have host"})

    @gen.coroutine
    def host_index_data(self, user_id, host_id):
        """主机首页数据"""
        res = {}
        # relation
        relation_info = yield self.db.query_one(SQL.get_user_host_relation(user_id, host_id))
        if relation_info:
            # host_info
            res["relation"] = relation_info
            host_info = yield self.db.query_one(SQL.get_host_info(host_id))
            host_info["update_time"] = host_info["update_time"].strftime('%Y-%m-%d %H:%M:%S')
            host_info["disk_stat"] = map(lambda i: [round(x, 2) if type(x) == float else x for x in i],
                                         eval(host_info["disk_stat"]))
            # 只筛选5G以上的磁盘信息(去掉虚拟磁盘的干扰)
            host_info["disk_stat"] = filter(lambda x: x[2] > 5, host_info["disk_stat"])
            host_info["disk_total_size"] = round(  # 磁盘总量求和
                reduce(lambda x, y: x + y, map(lambda x: x[2], host_info["disk_stat"])), 2)
            host_info["CPU_info"] = eval(host_info["CPU_info"])
            res["host_info"] = host_info
            # host_records
            host_records = yield self.db.query(SQL.get_host_records(host_id, 50))
            for r in host_records:
                r["record_time"] = r["record_time"].strftime('%Y-%m-%d %H:%M:%S')
                r["CPUs"] = eval(r["CPUs"])
            res["host_records"] = host_records
            res["host_now_record"] = host_records[0]
            res["record_time"] = res["host_now_record"]["record_time"] if res["host_now_record"]["record_time"] > \
                                                                          host_info["update_time"] else host_info[
                "update_time"]

            raise gen.Return(res)
        else:
            raise gen.Return({"error": "no host"})

    @gen.coroutine
    def delete_host(self, user_id, host_id):
        """删除用户与主机的关联"""
        yield self.db.execute(SQL.delete_user_host_relation(user_id, host_id))

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

    @gen.coroutine
    def all_user_process_relation(self, user_id):
        """获取所有用户关联进程"""
        res = {}
        # relation
        relations = yield self.db.query(SQL.get_user_all_process_relation(user_id))
        if relations:
            res["relation"] = relations
            for p in res["relation"]:
                pi = yield self.db.query_one(SQL.get_process_info(p["process_id"]))
                hi = yield self.db.query_one(SQL.get_host_info(p["host_id"]))
                select_btn_str = "#" + str(p["process_id"]) + " | " + p["type"] + "(" + p["comment"] + ", pid=" + \
                                 str(pi["pid"]) + ")" + " @ " + hi["host"]
                p["select_str"] = select_btn_str
            raise gen.Return(res)
        else:
            raise gen.Return({"error": "user dont have any process !"})

    @gen.coroutine
    def process_index_data(self, user_id, process_id):
        """进程首页数据"""
        res = {}
        # relation
        relation_info = yield self.db.query_one(SQL.get_user_process_relation(user_id, process_id))
        if relation_info:
            # process at host
            host_info = yield self.db.query_one(SQL.get_host_info(relation_info["host_id"]))
            host_info["update_time"] = host_info["update_time"].strftime('%Y-%m-%d %H:%M:%S')
            res["host_info"] = host_info
            # process_info
            res["relation"] = relation_info
            process_info = yield self.db.query_one(SQL.get_process_info(process_id))
            process_info["update_time"] = process_info["update_time"].strftime('%Y-%m-%d %H:%M:%S')
            process_info["log_path"] = process_info["log_path"] if process_info["log_path"] else "暂无"
            process_info["process_path"] = process_info["process_path"] if process_info["process_path"] else "暂无"
            res["process_info"] = process_info
            # process_records
            process_records = yield self.db.query(SQL.get_process_records(process_id, 288))
            for r in process_records:
                r["record_time"] = r["record_time"].strftime('%Y-%m-%d %H:%M:%S')
            res["process_records"] = process_records
            res["host_now_record"] = process_records[0]
            res["record_time"] = res["host_now_record"]["record_time"] if res["host_now_record"]["record_time"] > \
                                                                          process_info["update_time"] else process_info[
                "update_time"]
            raise gen.Return(res)
        else:
            raise gen.Return({"error": "no process"})

    @gen.coroutine
    def delete_process(self, user_id, process_id):
        """删除用户与进程的关联"""
        yield self.db.execute(SQL.delete_user_process_relation(user_id, process_id))

    # alert
    @gen.coroutine
    def alert_user_data(self, uid):
        """告警页面展示信息"""
        res = {}
        # host
        res["user_host_relation"] = yield self.db.query(SQL.get_user_all_host_relation(uid))
        for host_relation in res["user_host_relation"]:
            host_info = yield self.db.query_one(SQL.get_host_info(host_relation["host_id"]))
            host_alert_rule = yield self.db.query_one(SQL.get_host_alert_rule(host_relation["host_id"]))
            if host_info and "update_time" in host_info:
                host_info.pop("update_time")
            if host_alert_rule and "update_time" in host_alert_rule:
                host_alert_rule.pop("update_time")
            host_relation["host_info"] = host_info
            host_relation["host_alert_rule"] = host_alert_rule
        # process
        res["user_process_relation"] = yield self.db.query(SQL.get_user_all_process_relation(uid))
        for process_relation in res["user_process_relation"]:
            process_info = yield self.db.query_one(SQL.get_process_info(process_relation["process_id"]))
            process_alert_rule = yield self.db.query_one(SQL.get_process_alert_rule(process_relation["process_id"]))
            if process_info and "update_time" in process_info:
                process_info.pop("update_time")
            if process_alert_rule and "update_time" in process_alert_rule:
                process_alert_rule.pop("update_time")
                if not process_alert_rule["log_key_words"]:
                    process_alert_rule["log_key_words"] = "\"\""
            process_relation["process_info"] = process_info if process_info else {}
            process_relation["process_alert_rule"] = process_alert_rule if process_alert_rule else {}
        raise gen.Return(res)

    # alert
    @gen.coroutine
    def update_alert_rule(self, uid, request_json):
        """更新告警规则"""

        # format user
        def str2int_for_rule(s):
            if type(s) == str:
                if not s:
                    return -1
                elif s.isdigit():
                    return int(s)
                else:
                    return -1
            else:
                return -1

        for k in request_json.keys():
            if k != "log_key_words":
                request_json[k] = str2int_for_rule(request_json[k])

        # 查询是否存在
        exist = yield self.db.query_one(
            SQL.get_alert_rule_by_uid_hid_pid(uid, request_json["host_id"], request_json["process_id"]))

        if exist:
            self.db.execute(SQL.update_alert_rule(uid, rules=request_json))
        else:
            self.db.execute(SQL.add_alert_rule(uid, rules=request_json))

        raise gen.Return(request_json)
