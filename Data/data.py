#!/usr/bin/env python
# encoding:utf8

"""
Watch_Dogs
业务逻辑
"""

from tornado import gen

from remote_control_ssh import *
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
    def update_user_info(self, user_id, update_field, update_value):
        """更新用户信息"""
        for k, v in zip(update_field, update_value):
            if k == "password":
                yield self.db.execute(SQL.update_user_info(user_id, k, self.prpcrypt.encrypt(v)))
            else:
                yield self.db.execute(SQL.update_user_info(user_id, k, v))

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
            for key in ["system", "kernel", "intranet_ip", "extranet_ip", "default_net_device"]:
                if not host_info[key]:  # 针对刚刚添加的主机
                    host_info[key] = "目前暂无数据"
            host_info["update_time"] = host_info["update_time"].strftime('%Y-%m-%d %H:%M:%S')
            if host_info["disk_stat"]:
                host_info["disk_stat"] = map(lambda i: [round(x, 2) if type(x) == float else x for x in i],
                                             eval(host_info["disk_stat"]))
                # 只筛选5G以上的磁盘信息(去掉虚拟磁盘的干扰)
                host_info["disk_stat"] = filter(lambda x: x[2] > 5, host_info["disk_stat"])
                host_info["disk_total_size"] = round(  # 磁盘总量求和
                    reduce(lambda x, y: x + y, map(lambda x: x[2], host_info["disk_stat"])), 2)
            else:
                host_info["disk_stat"] = []
                host_info["disk_total_size"] = 0
            if host_info["CPU_info"]:
                host_info["CPU_info"] = eval(host_info["CPU_info"])
            else:
                host_info["CPU_info"] = []
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
    def add_host(self, uid, **request_json):
        """添加主机"""
        res = []
        host_exist = yield self.db.query_one(SQL.check_host_exist(request_json["host_ip"], request_json["host_user"]))
        # 添加主机记录, 获取主机id
        if not host_exist:  # 尚未添加过主机
            yield self.db.execute(SQL.add_host_info(request_json["host_ip"], request_json["host_user"],
                                                    self.prpcrypt.encrypt(request_json["host_password"]),
                                                    request_json["host_port"]))
            host_id = yield self.db.query_one(SQL.check_host_exist(request_json["host_ip"], request_json["host_user"]))
            host_id = host_id["host_id"]
            res.append("[OK] 主机记录添加成功, 当前主机ID为{host_id}".format(host_id=host_id))
            # 初始化主机记录
            yield self.db.execute(SQL.insert_host_record_error(host_id))
            res.append("[OK] 主机资源记录初始化...成功")
        else:  # 添加过主机
            host_id = host_exist["host_id"]
            res.append("[WARN] 主机记录添加成功, 此主机已经被监控过")
        # 添加用户与主机记录
        relation_exist = yield self.db.query_one(SQL.check_user_host_relation(uid, host_id))
        if not relation_exist:  # 尚未添加过记录
            yield self.db.query_one(
                SQL.add_user_host_relation(uid, host_id, request_json["host_comment"], request_json["host_type"]))
            res.append("[OK] 主机与当前用户关联关系添加...成功")
        else:  # 添加过记录
            res.append("[WARN] 用户已经关注了当前主机")
        # 远程部署客户端, 改为用户自行部署
        res.append("[手动部署] 由于自动化部署时间过长, 容易出现http链接断开的异常, 请手动登录该虚拟机并登录到root")
        res.append("[手动部署] 执行如下命令 curl http://10.245.146.202:8013/client/ClientSetup.sh | sh")
        res.append("[手动部署] 待命令执行完毕后, 系统当前路径的 .Watch_Dogs-Client 文件夹下")
        res.append("[手动部署] 并且系统会新增一个名为 python -u Watch_Dogs-Client.py 的进程, 此为监控进程, 切勿关闭")
        res.append("[手动部署] 完成后, 刷新当前页面并选择新添加的主机之后, 点击下方的更新信息即可获取当前主机的相关数据")
        res.append("[OK] 主机添加完成, 请根据上方提示进行操作后刷新")
        raise gen.Return({"result": res})

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
    def add_process(self, **request_json):
        """增加进程"""
        yield self.db.execute(
            SQL.add_watch_process(request_json["new_process_at_host_id"], request_json["new_process_pid"]
                                  , request_json["new_process_log_path"], request_json["new_process_path"]
                                  , request_json["new_process_start_com"]))

    @gen.coroutine
    def add_user_process_relation(self, uid, **request_json):
        process_id = yield self.db.query_one(
            SQL.get_process_id(request_json["new_process_at_host_id"], request_json["new_process_pid"]))
        yield self.db.execute(SQL.add_user_process_relation(
            uid, request_json["new_process_at_host_id"], process_id["process_id"], request_json["new_process_comment"],
            request_json["new_process_type"]
        ))

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
            process_info["start_com"] = process_info["start_com"] if process_info["start_com"] else "暂无"
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

    # Alert

    @gen.coroutine
    def alert_user_data(self, user_id):
        """告警页面展示信息"""
        res = {}
        # host
        res["user_host_relation"] = yield self.db.query(SQL.get_user_all_host_relation(user_id))
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
        res["user_process_relation"] = yield self.db.query(SQL.get_user_all_process_relation(user_id))
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

    @gen.coroutine
    def update_alert_rule(self, user_id, request_json):
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
            SQL.get_alert_rule_by_uid_hid_pid(user_id, request_json["host_id"], request_json["process_id"]))

        if exist:
            self.db.execute(SQL.update_alert_rule(user_id, rules=request_json))
        else:
            self.db.execute(SQL.add_alert_rule(user_id, rules=request_json))

        raise gen.Return(request_json)

    # Manage

    def update_process_info(self, user_id, process_id, request_json):
        """更新进程信息"""
        self.db.execute(SQL.update_user_host_relation(user_id, process_id, request_json["process_type"],
                                                      request_json["process_comment"]))
        self.db.execute(
            SQL.update_host_info_from_web(process_id, request_json["process_log_path"], request_json["process_path"],
                                          request_json["process_start_com"], request_json["process_pid_for_update"]))

    @gen.coroutine
    def close_process(self, process_id, pid):
        """关闭进程"""
        pi = yield self.db.query_one(SQL.get_process_info(process_id))
        hi = yield self.db.query_one(SQL.get_host_info(pi["host_id"]))
        host, user, password, port = hi["host"], hi["user"], self.prpcrypt.decrypt(hi["password"]), hi["port"]
        self.db.execute(SQL.update_process_info_not_exit(process_id))
        res = kill_process(host, user, password, port, pid=pid)
        if res["status"] == "OK":
            raise gen.Return({"result": "进程关闭成功"})
        else:
            raise gen.Return({"result": "进程关闭出现问题, 请登录远程服务器自行检查"})

    @gen.coroutine
    def restart_process(self, process_id, pid):
        """重启进程"""
        pi = yield self.db.query_one(SQL.get_process_info(process_id))
        path, start_cmd = pi["process_path"], pi["start_com"]
        hi = yield self.db.query_one(SQL.get_host_info(pi["host_id"]))
        hid, host, user, password, port = hi["host_id"], hi["host"], hi["user"], self.prpcrypt.decrypt(hi["password"]), \
                                          hi["port"]
        if path.strip() == "" and start_cmd.strip() == "":  # 记录不全
            raise gen.Return({"result": "错误, 进程地址或启动命令未记录"})
        # 重启
        res = kill_process(host, user, password, port, pid=pid)
        if res["status"] == "OK":
            res = start_process(host, user, password, port, process_path=path, start_cmd=start_cmd)
            if res["status"] == "OK":
                raise gen.Return({"result": "进程启动成功", "start_com": start_cmd, "host_id": hid})
            else:
                raise gen.Return({"result": "进程重启失败(启动失败)"})
        else:
            raise gen.Return({"result": "进程重启失败(关闭失败)"})
        # 获取新的pid并更新数据库中的记录
