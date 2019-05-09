#!/usr/bin/env python
# encoding:utf8

"""
Watch_Dogs
远程资源监控预警功能
"""

import json
import time

import schedule

from conf import setting
from models.SQL_generate import SQL
from models.db_opreation import DataBase
from client_manage import ClientManager
from send_alert_email import send_alert_email

Setting = setting.Setting()
logger_client_manage = Setting.logger


class AlertMonitor(object):
    """远程资源监控告警"""

    # Singleton
    _instance = None

    def __new__(cls, *args, **kw):
        """单例模式"""
        if not cls._instance:
            cls._instance = super(AlertMonitor, cls).__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        """构造函数"""
        self.db = DataBase()
        self.client_manage = ClientManager()

    def update_alert_rule_relate_record_id(self, aid, rid):
        """更新告警记录最后对应的资源记录id(防止多次告警)"""
        with self.db as db:
            db.execute_no_return(SQL.update_alert_rule_last_relate_record_id(aid, rid))
            db.commit()

    def get_last_host_record(self, hid):
        """获取最近一次的主机资源"""
        with self.db as db:
            return {"host_record": db.query_one(SQL.get_host_recent_record(hid)),
                    "host_info": db.query_one(SQL.get_host_info(hid))}

    def get_last_process_record(self, pid):
        """获取最近一次的进程资源记录"""
        with self.db as db:
            return {"process_record": db.query_one(SQL.get_process_recent_record(pid)),
                    "process_info": db.query_one(SQL.get_process_info(pid))}

    def get_user_email_address_and_name(self, uid):
        """获取用户收取告警用户名及邮件地址"""
        with self.db as db:
            return db.query_one(SQL.get_user_alert_address(uid))

    def get_all_alert_rules(self):
        """获取所有监控规则"""
        with self.db as db:
            return {"host_rules": db.execute(SQL.get_all_host_alert_rules()),
                    "process_rules": db.execute(SQL.get_all_process_alert_rules())}

    def host_status_detect(self, host_rules):
        """主机告警规则匹配"""
        for host_rule in host_rules:
            # 获取预警规则
            aid, uid, hid, pid, sd, cl, cg, ml, mg, nul, nug, ndl, ndg, kws, lrid, _ = host_rule
            # 获取主机数据
            hnr = self.get_last_host_record(hid)
            hnr["host_info"]["update_time"] = hnr["host_info"]["update_time"].strftime('%Y-%m-%d %H:%M:%S')
            hnr["host_record"]["record_time"] = hnr["host_record"]["record_time"].strftime('%Y-%m-%d %H:%M:%S')
            hi = hnr["host_info"]
            hr = hnr["host_record"]
            hrid = hnr["host_record"]["record_id"]
            # 跳过记录不全的主机
            if not (hi and hr):
                continue
            # 跳过上次告警过的记录
            if hrid == lrid:
                continue
            state, cpu, mem, nu, nd = hi["status"], hr["CPU"], hr["mem"], hr["net_upload_kbps"], hr["net_download_kbps"]
            # 预警地址获取
            host_name = "#" + str(hi["host_id"]) + " | " + str(hi["user"]) + "@" + str(hi["host"])
            ui = self.get_user_email_address_and_name(uid)
            user_name, user_email = ui["user"], ui["email"]
            # 状态检测
            if sd and sd != -1:
                if not state:
                    send_alert_email(user_email, user_name, host_name, "主机状态异常", json.dumps(hnr, indent=2))
                    self.update_alert_rule_relate_record_id(aid, hrid)
                    continue
            # cpu
            if cl != -1:
                if cpu < cl:
                    send_alert_email(user_email, user_name, host_name, "CPU占用率小于" + str(cl), json.dumps(hnr, indent=2))
                    self.update_alert_rule_relate_record_id(aid, hrid)
                    continue
            if cg != -1:
                if cpu > cg:
                    send_alert_email(user_email, user_name, host_name, "CPU占用率大于" + str(cg), json.dumps(hnr, indent=2))
                    self.update_alert_rule_relate_record_id(aid, hrid)
                    continue
            # mem
            if ml != -1:
                if mem < ml:
                    send_alert_email(user_email, user_name, host_name, "内存占用率小于" + str(ml), json.dumps(hnr, indent=2))
                    self.update_alert_rule_relate_record_id(aid, hrid)
                    continue
            if mg != -1:
                if mem > mg:
                    send_alert_email(user_email, user_name, host_name, "内存占用率大于" + str(mg), json.dumps(hnr, indent=2))
                    self.update_alert_rule_relate_record_id(aid, hrid)
                    continue
            # net_upload_kbps
            if nul != -1:
                if nu < nul:
                    send_alert_email(user_email, user_name, host_name, "网络上传速度(kbps)小于" + str(nul),
                                     json.dumps(hnr, indent=2))
                    self.update_alert_rule_relate_record_id(aid, hrid)
                    continue
            if nug != -1:
                if nu > nug:
                    send_alert_email(user_email, user_name, host_name, "网络上传速度(kbps)大于" + str(nug),
                                     json.dumps(hnr, indent=2))
                    self.update_alert_rule_relate_record_id(aid, hrid)
                    continue
            # net_download_kbps
            if ndl != -1:
                if nd < ndl:
                    send_alert_email(user_email, user_name, host_name, "网络下载速度(kbps)小于" + str(ndl),
                                     json.dumps(hnr, indent=2))
                    self.update_alert_rule_relate_record_id(aid, hrid)
                    continue
            if ndg != -1:
                if nd > ndg:
                    send_alert_email(user_email, user_name, host_name, "网络下载速度(kbps)大于" + str(ndg),
                                     json.dumps(hnr, indent=2))
                    self.update_alert_rule_relate_record_id(aid, hrid)
                    continue

    def process_status_detect(self, process_rules):
        """进程告警规则匹配"""
        for process_rule in process_rules:
            # 获取预警规则
            aid, uid, hid, pid, sd, cl, cg, ml, mg, nul, nug, ndl, ndg, kws, lrid, _ = process_rule
            # 获取主机数据
            pnr = self.get_last_process_record(hid)
            pnr["process_info"]["update_time"] = pnr["process_info"]["update_time"].strftime('%Y-%m-%d %H:%M:%S')
            pnr["process_record"]["record_time"] = pnr["process_record"]["record_time"].strftime('%Y-%m-%d %H:%M:%S')
            pi = pnr["process_info"]
            pr = pnr["process_record"]
            prid = pnr["process_record"]["record_id"]
            # 跳过记录不全的主机
            if not (pi and pr):
                continue
            # 跳过上次告警过的记录
            if prid == lrid:
                continue
            state, cpu, mem, nu, nd, log_path = pi["state"], pr["cpu"], pr["mem"], \
                                                pr["net_upload_kbps"], pr["net_download_kbps"], pi["log_path"]
            # # 预警地址获取
            process_name = "#" + str(pi["process_id"]) + " | " + str(pi["comm"]) + "(pid=" + str(
                pi["pid"]) + ") @ No." + str(pi["host_id"]) + " host"
            ui = self.get_user_email_address_and_name(uid)
            user_name, user_email = ui["user"], ui["email"]
            # 状态检测
            if sd and sd != -1:
                if state == "X":
                    send_alert_email(user_email, user_name, process_name, "进程不存在", json.dumps(pnr, indent=2))
                    self.update_alert_rule_relate_record_id(aid, prid)
                    continue
                elif state == "0":
                    send_alert_email(user_email, user_name, process_name, "进程状态获取失败", json.dumps(pnr, indent=2))
                    self.update_alert_rule_relate_record_id(aid, prid)
                    continue
            # cpu
            if cl != -1:
                if cpu < cl:
                    send_alert_email(user_email, user_name, process_name, "进程CPU占用率小于" + str(cl),
                                     json.dumps(pnr, indent=2))
                    self.update_alert_rule_relate_record_id(aid, prid)
                    continue
            if cg != -1:
                if cpu > cg:
                    send_alert_email(user_email, user_name, process_name, "进程CPU占用率大于" + str(cg),
                                     json.dumps(pnr, indent=2))
                    self.update_alert_rule_relate_record_id(aid, prid)
                    continue
            # mem
            if ml != -1:
                if mem < ml:
                    send_alert_email(user_email, user_name, process_name, "进程内存占用(M)小于" + str(ml),
                                     json.dumps(pnr, indent=2))
                    self.update_alert_rule_relate_record_id(aid, prid)
                    continue
            if mg != -1:
                if mem > mg:
                    send_alert_email(user_email, user_name, process_name, "进程内存占用(M)大于" + str(mg),
                                     json.dumps(pnr, indent=2))
                    self.update_alert_rule_relate_record_id(aid, prid)
                    continue
            # net_upload_kbps
            if nul != -1:
                if nu < nul:
                    send_alert_email(user_email, user_name, process_name, "进程网络上传速度(kbps)小于" + str(nul),
                                     json.dumps(pnr, indent=2))
                    self.update_alert_rule_relate_record_id(aid, prid)
                    continue
            if nug != -1:
                if nu > nug:
                    send_alert_email(user_email, user_name, process_name, "进程网络上传速度(kbps)大于" + str(nug),
                                     json.dumps(pnr, indent=2))
                    self.update_alert_rule_relate_record_id(aid, prid)
                    continue
            # net_download_kbps
            if ndl != -1:
                if nd < ndl:
                    send_alert_email(user_email, user_name, process_name, "进程网络下载速度(kbps)小于" + str(ndl),
                                     json.dumps(pnr, indent=2))
                    self.update_alert_rule_relate_record_id(aid, prid)
                    continue
            if ndg != -1:
                if nd > ndg:
                    send_alert_email(user_email, user_name, process_name, "进程网络下载速度(kbps)大于" + str(ndg),
                                     json.dumps(pnr, indent=2))
                    self.update_alert_rule_relate_record_id(aid, prid)
                    continue
            # 日志关键词
            if kws:
                key_words = kws.split(";")
                for kw in key_words:
                    res = self.client_manage.log_search_keyword(hid, log_path, kw)
                    if type(res) == dict and "search_result" in res:
                        if res["search_result"]:
                            send_alert_email(user_email, user_name, process_name, "进程日志发现告警关键词 :" + str(kw),
                                             "\n".join(res["search_result"]))
                            self.update_alert_rule_relate_record_id(aid, prid)
                            continue

    def alert_monitor(self):
        """监控工作"""
        rules = self.get_all_alert_rules()
        self.host_status_detect(rules["host_rules"])
        self.process_status_detect(rules["process_rules"])

    def alert_monitor_thread(self):
        """监控线程"""
        schedule.every(Setting.ALERT_INTERVAL_MIN).minutes.do(self.alert_monitor)
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == '__main__':
    AlertMonitor().alert_monitor()
