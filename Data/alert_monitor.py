#!/usr/bin/env python
# encoding:utf8

"""
Watch_Dogs
远程资源监控预警功能
"""

import time

import schedule

from conf import setting
from models.SQL_generate import SQL
from models.db_opreation import DataBase
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

    def get_last_host_record(self, hid):
        """获取最近一次的主机资源"""
        with self.db as db:
            return db.query_one(SQL.get_host_recent_record(hid))

    def get_last_process_record(self, pid):
        """获取最近一次的进程资源记录"""
        with self.db as db:
            return db.query_one(SQL.get_process_recent_record(pid))

    def get_user_email_address_and_name(self, uid):
        """获取用户收取告警用户名及邮件地址"""
        with self.db as db:
            res = db.query_one(SQL.get_user_alert_address(uid))

    def get_all_alert_rules(self):
        """获取所有监控规则"""
        with self.db as db:
            res = {}
            res["host_rules"] = db.execute(SQL.get_host_alert_rules())
            res["process_rules"] = db.execute(SQL.get_process_alert_rules())
            return res

    def host_status_detect(self, host_rules):
        """主机告警规则匹配"""

    def process_status_detect(self):
        """主机告警规则匹配"""

    def remote_monitor_thread(self):
        """监控线程"""
        rules = self.get_all_alert_rules()
        self.host_status_detect(rules["host_rules"])
        self.process_status_detect(rules["process_rules"])


if __name__ == '__main__':
    print AlertMonitor().get_all_alert_rules()
